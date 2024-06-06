from collections import defaultdict
import re
from django.forms import ValidationError

from .models import *

import pandas as pd 
import numpy as np
from io import BytesIO
import requests



class GoogleSheetProcessor:
    sheet_url = None
    sheet_key = None
    project_url = None
    episode_title = None
    
    excel_file = None 
    filename = None
    download_url = None
    bytes_data=  None
    
    all_sheets = {}
    
    # GOOGLE SHEET LINK DATA EXTRACTION
    def __init__(self, sheet, project_url:str, isFile:bool):
        
        if not isFile:
            self.sheet_url = sheet
            self.project_url = project_url
            self.sheet_key = self.filter_url(sheet)  
            self.load_google_sheet() # load all sheets  
            self.get_episode_title()
        else:
            self.project_url = project_url
            self.excel_file = sheet
            self.load_google_sheet_from_file()
            self.get_episode_title()
            
        
    # example sharing link
    # https://docs.google.com/spreadsheets/d/13FduNu5j0kNVUl2XGXbfiD1VPjQQr_ELXuL46G_Mzgk/edit?usp=sharing
    def filter_url(self, sheetSharingUrl: str):
        if "https://docs.google.com/spreadsheets/d/" in sheetSharingUrl:
            return sheetSharingUrl.replace("https://docs.google.com/spreadsheets/d/", "").split("/")[0]
        else:
            raise ValidationError("Invalid Google Sheets sharing link")
        
    def load_google_sheet(self):
        try:
            #Create a public URL
            #https://docs.google.com/spreadsheets/d/0Ak1ecr7i0wotdGJmTURJRnZLYlV3M2daNTRubTdwTXc/edit?usp=sharing
            self.download_url = f'https://docs.google.com/spreadsheet/ccc?key={self.sheet_key}&output=xlsx'

            #get spreadsheets key from url
            response = requests.get(self.download_url)
            data = response.content
            
            # extracting file name
            # Extract the filename from the content-disposition header
            d = response.headers.get('content-disposition')
            if d:
                # Handle both the standard filename and UTF-8 encoded filename
                filename = None
                matches = re.findall(r'filename\*?=([^;]+)', d)
                if matches:
                    filename = matches[-1].strip()
                    # Decode the UTF-8 encoded filename if necessary
                    if filename.startswith("UTF-8''"):
                        filename = filename[len("UTF-8''"):]
                        filename = requests.utils.unquote(filename)
                if filename is not None:
                    self.filename = filename.strip('"')
                else:
                    raise ValidationError("Google Sheets File Provided has no name separated by '[EPISODE TITLE] - [TOOL NAME] - [STATUS]'")
            else:
                raise ValidationError("Google Sheets File Provided has no name separated by '[EPISODE TITLE] - [TOOL NAME] - [STATUS]'")

            print(f"Filename: {self.filename}")
            
            # loading in bytes
            self.bytes_data = BytesIO(data)
            
            # Create an empty list to store DataFrames
            self.all_sheets = {}
            self.excel_file = pd.ExcelFile(self.bytes_data)
            
            # Read all sheets using a loop
            for sheet_name in self.excel_file.sheet_names:
                df = pd.read_excel(self.bytes_data, sheet_name=sheet_name, header=0)
                self.all_sheets[sheet_name] = df
        except Exception as ex:
            raise ValidationError("Unable to load xslx file.")
    
    def load_google_sheet_from_file(self):
        try:
            # extracting file name
            data = self.excel_file
            
            self.filename = data._name
            self.sheet_url = self.filename
            
            print(f"Filename: {self.filename}")
            
            # Create an empty list to store DataFrames
            self.all_sheets = {}
            self.excel_file = pd.ExcelFile(self.excel_file)
            
            # Read all sheets using a loop
            for sheet_name in self.excel_file.sheet_names:
                df = pd.read_excel(data, sheet_name=sheet_name, header=0)
                self.all_sheets[sheet_name] = df
        except Exception as ex:
            raise ValidationError("Unable to load xslx file.")
    
    
    def get_episode_title(self):
        filename = self.filename
        self.episode_title = filename.split("-")[0].strip()
        print(f"Episode Title: {self.episode_title}")
        
        
    
    def save_full_episode_series_sequence(self, user):
        
        sequences_sheet = self.all_sheets.get("Copy CSV Here", None)
        chapters_filtered_sheet = self.all_sheets.get("Chapter Filtered", None)
        if sequences_sheet is None or chapters_filtered_sheet is None:
            raise ValidationError("Sheets Contain Invalid Episode Data!")
        
        # joining both datasets
        # Convert relevant columns to string
        sequences_sheet['Start Time'] = sequences_sheet['Start Time'].astype(str)
        sequences_sheet['End Time'] = sequences_sheet['End Time'].astype(str)
        sequences_sheet['Text'] = sequences_sheet['Text'].astype(str)

        chapters_filtered_sheet['Start Time'] = chapters_filtered_sheet['Start Time'].astype(str)
        chapters_filtered_sheet['End Time'] = chapters_filtered_sheet['End Time'].astype(str)
        chapters_filtered_sheet['Text'] = chapters_filtered_sheet['Text'].astype(str)
        
        # Fill missing values in Chapters and Reel columns with appropriate defaults (e.g., empty string or zero)
        chapters_filtered_sheet['Chapter'] = chapters_filtered_sheet['Chapter'].fillna(0).astype(int)
        chapters_filtered_sheet['Reel'] = chapters_filtered_sheet['Reel'].fillna(0).astype(int)

        # Combine both DataFrames using the 'outer' join to ensure no data is lost
        combined_df = pd.merge(sequences_sheet, 
                            chapters_filtered_sheet[['Start Time', 'End Time', 'Text', 'Chapter', 'Reel']],
                            on=['Start Time', 'End Time', 'Text'], 
                            how='outer')
        
        combined_df['Chapter'] = combined_df['Chapter'].fillna(0).astype(int)
        combined_df['Reel'] = combined_df['Reel'].fillna(0).astype(int)
        
        # combined_df.to_excel('combined_data.xlsx', index=False)
        
        print("LOOP Started")
        episode_sequence = []
        
        episode_model = EpisodeModel.objects.create(
            title=self.episode_title,
            content="",
            user=user,
            start_time=None,
            end_time=None,
            sheet_link=self.sheet_url,
            project_link=self.project_url
        )
        episode_content = ""
        
        sequence_models = []
        chapters_models = {}
        chapters_sequences_id = {}
        chapter_contents = {}
        reels_contents = {}
        
        reel_models = {}
        reels_sequences_id = {}
        
        index = 0
        for row in combined_df.itertuples(index=True, name='Pandas'):
            index = row.Index
            sequence_number = row.Index + 1
            words = row.Text 
            start_time = row._2
            end_time = row._3
            chapter = row.Chapter
            reel = row.Reel
            
            # adding data to episode model
            if episode_model.start_time is None:
                episode_model.start_time = start_time
            episode_model.end_time = end_time
            
            episode_content = episode_content + " " + words.strip()
            
            # creating current sequence model
            sequence_uid = uuid.uuid4()
            sequence_model = SequenceModel(
                id = sequence_uid,
                episode=episode_model,
            user=user,
                words=words,
                sequence_number=sequence_number,
                start_time=start_time,
                end_time=end_time
            )
            sequence_models.append(sequence_model)
            
            if chapter != 0:
                if str(chapter) not in chapters_models:
                    chapter_uid = uuid.uuid4()
                    chapter_model = ChapterModel(
                        id = chapter_uid,
                        episode = episode_model,
                        user=user,
                        title = f"Chapter {str(chapter)}",
                        chapter_number = int(chapter),
                        content = words.strip(),
                        start_time = start_time,
                        end_time = end_time,
                    )
                    chapter_model.save()
                    # chapter_model.sequences.add(sequence_model)
                    chapters_models[str(chapter)] = chapter_model
                else:
                    chapter_model = chapters_models[str(chapter)]
                    # chapter_model.content = chapter_model.content + " " + words.strip()
                    chapter_model.end_time = end_time
                    # chapter_model.sequences.add(sequence_model)
                    chapters_models[str(chapter)] = chapter_model

                if str(chapter) not in chapters_sequences_id:
                    chapters_sequences_id[str(chapter)] = []
                    chapter_contents[str(chapter)]  = ""
                
                chapter_contents[str(chapter)] += " " + words.strip()
                chapters_sequences_id[str(chapter)].append(sequence_uid)
            
            if reel != 0:
                
                if f"{str(chapter)}-{str(reel)}" not in reel_models:
                    reel_uid = uuid.uuid4()
                    reel_model = ReelModel(
                        id = reel_uid,
                        episode = episode_model,
                        user=user,
                        chapter = chapters_models[str(chapter)],
                        title = f"Reel {str(reel)}",
                        reel_number = int(reel),
                        content = words.strip(),
                        start_time = start_time,
                        end_time = end_time,
                    )
                    reel_model.save()
                    # reel_model.sequences.add(sequence_model)
                    reel_models[f"{str(chapter)}-{str(reel)}"] = reel_model
                else:
                    reel_model = reel_models[f"{str(chapter)}-{str(reel)}"]
                    # reel_model.content = reel_model.content + " " + words.strip()
                    reel_model.end_time = end_time
                    # reel_model.sequences.add(sequence_model)
                    reel_models[f"{str(chapter)}-{str(reel)}"] = reel_model
                
                
                if f"{str(chapter)}-{str(reel)}" not in reels_sequences_id:
                    reels_sequences_id[f"{str(chapter)}-{str(reel)}"] = []
                    reels_contents[f"{str(chapter)}-{str(reel)}"]  = ""

                reels_contents[f"{str(chapter)}-{str(reel)}"]  += " " + words.strip()
                
                reels_sequences_id[f"{str(chapter)}-{str(reel)}"].append(sequence_uid)
            
            # print(f"Index: {row.Index}")
            # print(f"Start Time: {row._1}, End Time: {row._2}, Text: {row._3}, Chapter: {row._4}, Reel: {row._5}")
        # Perform your operations here
        print("LOOP Completed")
        
        # Bulk create sequences
        SequenceModel.objects.bulk_create(sequence_models)
        print("Sequences Entered")
        
        # adding sequences 
        for chapterKey, chapterModel in chapters_models.items():
            print(chapterModel)
            chapterModel.content = chapter_contents[chapterKey]
            chapterModel.save()
            for sequence_id in chapters_sequences_id[chapterKey]:
                chapterModel.sequences.add(SequenceModel.objects.get(id = sequence_id))
        
        
        for reelKey, reelModel in reel_models.items():
            print(reelModel)
            reelModel.content = reels_contents[reelKey]
            reelModel.save()
            for sequence_id in reels_sequences_id[reelKey]:
                reelModel.sequences.add(SequenceModel.objects.get(id = sequence_id))
                
        # Save the final state of episode_model
        episode_model.content = episode_content
        episode_model.save()

    
        
    
    def __str__(self) -> str:
        all_str = {}
        for sheet, df in self.all_sheets.items():
            all_str[sheet] = df.shape
        
        return all_str.__str__()