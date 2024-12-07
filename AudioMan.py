# convert wav tot flac file
import os
import time
import warnings
import math
from pydub import AudioSegment
import shutil
from typing import Union, Optional, Tuple, Dict, List
from collections import Counter
from natsort import natsorted


INPUT_DIR = 'audio'
INPUT_FILE = 'audio/fwj.mp3'
OUPUT_DIR = 'output_segments'



'''
To Do:
    - Add padding feature for files that fell short for the duration
    - regex feature
    - allow user to decide if they wish to not make new directories automatically.
    - overwrite feature in split_audio_file(s) :done:
    - posn, pnos... thing in split_audio_files_as_well
'''


class AudioMan:
    
    supported_audio_formats = {
        '.mp3': 'mp3',
        '.wav': 'wav',
        '.ogg': 'ogg',
        '.flac': 'flac',
        '.m4a': 'm4a'
    }
    
    def __init__(self):
        pass


    @staticmethod
    def get_files_from_dir (dir: str):
        if not os.path.isdir(dir):
            raise FileNotFoundError("Given directory does not exist")
        
        all_items_in_dir = os.listdir(dir)
        files = [file for file in all_items_in_dir if os.path.isfile(os.path.join(dir, file))]
        
        return files


    @staticmethod
    def get_sorted_files (dir: str):
        if not os.path.isdir(dir):
            raise FileNotFoundError("Given directory does not exist")
        
        sorted_files = natsorted(AudioMan.get_files_from_dir(dir))
        return sorted_files


    @staticmethod
    def get_number_of_segments(audio: AudioSegment,
                               segment_duration_secs):
        
        total_duration = len(audio) # in milliseconds (ms)
        segment_length_ms = int(segment_duration_secs * 1000)
        num_segments = math.ceil(total_duration / segment_length_ms)
        
        return num_segments
    
    
    @staticmethod
    def get_duration(audio_path : str = None, 
                     audio_data : AudioSegment = None) -> float:
        
        if audio_path is None:
            if audio_data is None:
                raise ValueError("pass either audio_path or its audio_data")
            else:
                return audio_data.duration_seconds
        else:
            if not os.path.exists(audio_path):
                raise FileNotFoundError(f"Input file not found: {audio_path}")
            
            file_ext = os.path.splitext(audio_path)[1].lower()
            if file_ext not in AudioMan.supported_audio_formats:
                raise ValueError(f"Unsupported input file format: {file_ext}")
            
            try:
                audio_data = AudioSegment.from_file(audio_path, 
                                                    format=AudioMan.supported_audio_formats[file_ext])
            except Exception as e:
                raise RuntimeError(f"Error loading audio file: {e}")
            
            return audio_data.duration_seconds


    @staticmethod    
    def _create_segment (audio: AudioSegment, 
                         from_sec: Union[int, float],
                         to_sec: Union[int, float]):
        
        if from_sec > to_sec:
            raise IndexError("from_sec cannot be greater than to_sec")
        
        t1 = from_sec * 1000
        t2 = to_sec   * 1000
        segment = audio[t1:t2]
        
        return segment
        
        
        

    @staticmethod
    def split_audio_file(
        input_path: str, 
        segment_duration_secs: Union[int, float] = 60, 
        output_dir: Optional[str] = None,
        keep_output_format: bool = True,
        output_format: Optional[str] = None,
        output_prefix: Optional[str] = "",
        output_suffix: Optional[str] = "",
        delim: Optional[str] = '_',
        nomenclature: str = "pns",
        start_number: int = 1,
        jump_by: int = 1,
        keep_consistent_num_length: bool = False,
        drop_last: bool = False,
        overwrite: bool = False
    ) -> int:
        
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"Input file not found: {input_path}")


        file_ext = os.path.splitext(input_path)[1].lower()
        if file_ext not in AudioMan.supported_audio_formats:
            raise ValueError(f"Unsupported input file format: {file_ext}")

        if output_dir is None:
            output_dir = os.path.dirname(input_path) or '.' # if the input is in a dir then good 
                                                            # else put it in the current directory
        os.makedirs(output_dir, exist_ok=True)
        
        
        
        # nomenclature
        nomenclatures = ['n', 
                         'on', 'no', 'pns', 
                         'pons', 'pnos', 'opns', 'npos', 'posn', 'pnso']    
        nomenclature = nomenclature.lower()
        if nomenclature not in nomenclatures:
            raise ValueError(f"Invalid nomenclature provided. Can only be any of {nomenclatures}")
           
        
        # Validating Output Format
        if (not keep_output_format) and (output_format is None):
            raise ValueError("no output format specified. " + \
                             "Cannot set keep_output_format " + \
                             "False and output_format None at the same time")
        
        if (keep_output_format == True) and (output_format is not None):
            output_format = file_ext[1:]
            warnings.warn("Ignoring output format as keep_output_format has a greater priority")
        elif (not keep_output_format) and (output_format is not None):            
            output_format = output_format[1:] if (output_format[0] == '.') else output_format
            if ('.' + output_format) not in AudioMan.supported_audio_formats:
                raise ValueError(f"Unsupported input file format: {file_ext}")
        else:
            output_format = file_ext[1:]


        # Validate segment duration
        if segment_duration_secs <= 0:
            raise ValueError("Segment duration must be a positive number")

        # Load audio file
        try:
            audio = AudioSegment.from_file(input_path, format=AudioMan.supported_audio_formats[file_ext])
        except Exception as e:
            raise RuntimeError(f"Error loading audio file: {e}")

        # Calculate segment parameters
        total_duration = len(audio)  # in milliseconds
        segment_length_ms = int(segment_duration_secs * 1000)
        num_segments = math.ceil(total_duration / segment_length_ms)


        if drop_last == True:
            num_segments -= 1
        
        saved_files_count = 0
        if num_segments <= 0:
            warnings.warn("No segmentation possible. File is too small")
            return saved_files_count

        num_length = 0
        if keep_consistent_num_length == True:
            num_length = len(str(start_number + (num_segments - 1) * jump_by))
            
        file_num = start_number
        filename = os.path.basename(input_path)
        filename_wo_ext = os.path.splitext(filename)[0]
        
        # Split and export audio segments
        for i in range(num_segments):
            start_ms = i * segment_length_ms
            end_ms = min((i + 1) * segment_length_ms, total_duration)
            
            segment = audio[start_ms:end_ms]
            
            # Construct new filename
            file_numid = str(file_num).zfill(num_length)
            output_filename = []
            for name_comp in nomenclature:
                if name_comp == 'p':
                    output_filename.append(output_prefix)
                elif name_comp == 'o':
                    output_filename.append(filename_wo_ext)
                elif name_comp == 'n':
                    output_filename.append(file_numid)
                elif name_comp == 's':
                    output_filename.append(output_suffix)
            
            output_filename = delim.join(output_filename)
            output_filename += '.' + output_format
            
            file_num += jump_by
        
            output_path = os.path.join(output_dir, output_filename)
            
            if (os.path.exists(output_path)) and (not overwrite):
                warnings.warn(f"A file named {output_filename} already exists in the {output_dir}. " + \
                               "No overwrite permission given. " + \
                               "To allow overwriting, set overwrite=True")
                return saved_files_count
            
            # Export segment
            segment.export(output_path, format=output_format)
            saved_files_count += 1

        return saved_files_count
    
    
    
    
    def split_audio_files (
        input_dir: str,
        output_dir: Optional[str] = None,
        segment_duration_secs: Union[int, float] = 60, 
        keep_output_format: bool = True,
        extension_filter: Optional[List[str]] = None,
        output_format: Optional[str] = None,
        output_prefix: Optional[str] = "",
        output_suffix: Optional[str] = "",
        delim: Optional[str] = "_",
        nomenclature: str = "pns",
        keep_numbering_local: bool = True,
        start_number: int = 1,
        jump_by: int = 1,
        keep_consistent_num_length: bool = False,
        drop_last: bool = False,
        overwrite: bool = False
    )-> Tuple[int, Dict[str, int]]:
        
        input_files = AudioMan.get_sorted_files(input_dir)
        input_paths = [os.path.join(input_dir, input_file) for input_file in input_files]
        
        if not extension_filter:
            extension_filter = list(AudioMan.supported_audio_formats.keys())
        extension_filter = [f.lower() for f in extension_filter]
        
        warned = False
        valid_input_paths = []
        for input_path in input_paths:
            file_ext = os.path.splitext(input_path)[1].lower()
            if file_ext in AudioMan.supported_audio_formats:
                if file_ext in extension_filter:
                    valid_input_paths.append(input_path) 
            else:
                if not warned:
                    warnings.warn("The input directory contains some unsupported files. They are being skipped")
                    warned = True

        input_paths = valid_input_paths
        
        
        file_number = start_number
        total_saved_files_count = 0
        segments_count_by_file = {}
        for input_path in input_paths:
            segment_count = AudioMan.split_audio_file(input_path=input_path,
                                                      segment_duration_secs=segment_duration_secs,
                                                      output_dir=output_dir,
                                                      keep_output_format=keep_output_format,
                                                      output_format=output_format,
                                                      output_prefix=output_prefix,
                                                      output_suffix=output_suffix,
                                                      delim=delim,
                                                      nomenclature=nomenclature,
                                                      start_number=file_number,
                                                      jump_by=jump_by,
                                                      keep_consistent_num_length=keep_consistent_num_length,
                                                      drop_last=drop_last,
                                                      overwrite=overwrite
                                                    )
            total_saved_files_count += segment_count
            segments_count_by_file[os.path.basename(input_path)] = segment_count
            
            if not keep_numbering_local:
                file_number += segment_count
            else:
                file_number = start_number
        
        return total_saved_files_count, segments_count_by_file




    @staticmethod
    def total_rename (
        input_dir: str,
        rename_map: Optional[List[Tuple[str, str]]] = None,
        output_prefix: Optional[str] = "",
        output_suffix: Optional[str] = "",
        delim: str ="",
        nomenclature: Optional[str] = "posn",
        start_number: Optional[int] = None,
        jump_by: Optional[int] = None,
        keep_consistent_num_length: bool = False,
        extension_filter: Optional[List[str]] = None,
        overwrite: bool = False,
    ) ->int:
        
        renamed_files_count = 0
        # Explicit rename map takes highest priority
        if rename_map:
            for old_name, new_name in rename_map:
                
                old_path = os.path.join(input_dir, old_name)
                new_path = os.path.join(input_dir, new_name)
                
                if extension_filter:      
                    if os.path.splitext(old_name)[1].lower() not in extension_filter:
                        continue
                    if os.path.splitext(new_name)[1].lower() not in extension_filter:
                        continue
                
                if os.path.exists(old_path):
                    if (os.path.exists(new_path)) and (not overwrite):
                        warnings.warn(f"there already exists a file named '{new_name}' in '{input_dir}'. " + \
                                            "No overwrite permission given. " + \
                                            "If you want to overwrite, set overwrite=True")
                        return 0
                    
                    os.rename(old_path, new_path)
                    renamed_files_count += 1
                else:
                    raise FileNotFoundError(f"{old_name} does not exist")
            
            return renamed_files_count
        
        
        # Input validation
        if  input_dir is None:
            raise ValueError(f"no valid files source provided")
        
        all_files = AudioMan.get_sorted_files(input_dir)
        
        if extension_filter:
            extension_filter = [f.lower() for f in extension_filter]
            selected_ext_files = []
            for file in all_files:
                if os.path.splitext(file)[1].lower() in extension_filter:
                    selected_ext_files.append(file)
            
            all_files = selected_ext_files
            
        
        if not all_files:
            warnings.warn(f"no files in {input_dir}, with the given requirements, found")
            return 0
        
        
        nomenclatures = ['n', 
                         'on', 'no', 
                         'pos', 'pns', 
                         'pons', 'pnos', 'opns', 'npos', 'posn', 'pnso']    
        nomenclature = nomenclature.lower()
        if nomenclature not in nomenclatures:
            raise ValueError(f"Invalid nomenclature provided. Can only be any of {nomenclatures}")
        
        if 'n' in nomenclature:
            if start_number is None:
                start_number = 0
        else:
            if start_number is not None:
                warnings.warn(f"nomenclature doesn't contain 'n' but a start_number is given. " + \
                               "This is conflicting. This can give undesirable results. " + \
                               "No renaming possible")
                return 0
                
        if start_number is not None:
            current_number = start_number
            if jump_by is None:
                jump_by = 1            
        else:
            if jump_by is not None:
                warnings.warn('if you wish to number the files, set start_number as well.')
                return 0
            current_number = ''
            jump_by = ''
        
        
        num_length = 0
        if keep_consistent_num_length == True:
            if start_number is None:
                warnings.warn("Cannot request to keep consistent num length without " +\
                              "specifying a start_number and putting 'n' in the nomenclature. " +\
                              "If you wish to number the files, then please set start_number and jump_by as well.")
                return 0
            num_length = len(str(start_number + (len(all_files) - 1) * jump_by))
        
        
        for filename in all_files:
            # Get file extension
            file_ext = os.path.splitext(filename)[1]
            # if file_ext not in AudioMan.supported_audio_formats:
            #     raise ValueError(f"Unsupported input file format: {file_ext}")
            
            # Construct new filename
            file_numid = str(current_number).zfill(num_length)
            new_filename = []
            for name_comp in nomenclature:
                if name_comp == 'p':
                    new_filename.append(output_prefix)
                elif name_comp == 'o':
                    new_filename.append(os.path.splitext(filename)[0])
                elif name_comp == 'n':
                    new_filename.append(file_numid)
                elif name_comp == 's':
                    new_filename.append(output_suffix)
            
            new_filename = delim.join(new_filename)
            new_filename += file_ext
            
            # Source and destination paths
            src_path = os.path.join(input_dir, filename)
            dst_path = os.path.join(input_dir, new_filename)
            if src_path == dst_path:
                continue
            
            try:
                if os.path.exists(dst_path):
                    if not overwrite:
                        warnings.warn(f"there already exists a file named {new_filename} in {input_dir}. " + \
                                    "No overwrite permission given. " + \
                                    "If you want to overwrite, set overwrite=True")
                        return 0
                    else:
                        os.remove(dst_path)
            except PermissionError:
                print("File may be in use. Please close the file and try again")
                shutil.move(src_path, dst_path)
                renamed_files_count += 1
                current_number += jump_by
                continue
                
            
                
            # Copy or move file
            os.rename(src_path, dst_path)
            
            renamed_files_count += 1
            
            current_number += jump_by
        
        
        return renamed_files_count

            


    @staticmethod
    def change_extension (
        input_dir: str,
        from_ext: str,
        to_ext: str,
        make_copy=True,
        overwrite=False,
    ) -> int:
        if not os.path.isdir(input_dir):
            raise FileNotFoundError(f"{input_dir} doesn't exist")
        if from_ext not in AudioMan.supported_audio_formats:
            raise ValueError(f"change_extension doesn't support {from_ext}. Make sure all the extensions start with a '.', eg: .wav")
        if to_ext not in AudioMan.supported_audio_formats:
            raise ValueError(f"change_extension doesn't support {from_ext}. Make sure all the extensions start with a '.', eg: .wav")
        if from_ext == to_ext:
            warnings.warn(f"values of from_ext and to_ext are the same")
            return 0
        
        all_audio_files = AudioMan.get_files_from_dir(input_dir)
        all_audio_files = list(filter(lambda x: os.path.splitext(x)[1].lower() == from_ext.lower(), all_audio_files))
        
        rename_count = 0
        for file in all_audio_files:
            # Load audio file
            file_path = os.path.join(input_dir, file)
            try:
                audio = AudioSegment.from_file(file_path, format=AudioMan.supported_audio_formats[from_ext])
            except Exception as e:
                raise RuntimeError(f"Error loading audio file: {e}")
            
            output_path = os.path.splitext(file_path)[0] + to_ext
            if (os.path.exists(output_path)) and (not overwrite):
                warnings.warn(f"there already exists a file named {os.path.basename(output_path)} " + \
                                    "in the destination. No overwrite permission given. " + \
                                    "If you want to overwrite, set overwrite=True")
                return 0
            
            audio.export(output_path, format=AudioMan.supported_audio_formats[to_ext])
            
            if not make_copy:
                os.remove(file_path)
                
            rename_count += 1
        
        return rename_count