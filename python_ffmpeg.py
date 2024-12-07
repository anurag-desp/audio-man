import os
from pydub import AudioSegment



# def segment_audio_by_duration (audio_filepath, 
#                                destination_dir, 
#                                duration=10,
#                                output_prefix="segment_", 
#                                output_file_format ='wav'):
    
#     ffmpeg_command = f'''
#     ffmpeg -i {audio_filepath} -f segment -segment_time {duration} -c copy {destination_dir}/{output_prefix}%03d.{output_file_format}'''
    
#     print("Running...")
#     print(ffmpeg_command)
    
#     os.system(ffmpeg_command)


# segment_audio_by_duration(audio_filepath='audio/fwj.mp3',
#                           destination_dir='output_segments',
#                           output_prefix='fwj_seg_',
#                           output_file_format='wav')






##################
#     D U M P    #
##################
'''
 @staticmethod
    def complex_copy (
        input_dir: Optional[str] = None,
        rename_map: Optional[List[Tuple[str, str]]] = None,
        file_unq_ids: Optional[List[str]] = None,
        output_prefix: Optional[str] = None,
        output_suffix: Optional[str] = None,
        delim: str ="",
        start_number: int = 1,
        jump_by: int = 1,
        output_dir: Optional[str] = None,
        inplace: bool = False,
        extension_filter: Optional[List[str]] = None,
        overwrite: bool = False,
    ) -> int:
        """
        Rename files with multiple flexible options and priority.

        Priority of renaming parameters (highest to lowest):
        1. Explicit rename_map (if provided)
        2. Prefix/Suffix + Numbering
        3. Original filenames preserved

        Args:
            input_dir (str): Directory containing source files
            rename_map (List[Tuple[str, str]], optional): Explicit mapping of old to new filenames
            file_unq_ids: Optional[List[str]]: Explicit ordered ids for each new file
            output_prefix (str, optional): Prefix to add to renamed files
            output_suffix (str, optional): Suffix to add to renamed files
            start_number (int, optional): Starting number for numbered files. Defaults to 1.
            jump_by (int, optional): Increment between numbers. Defaults to 1.
            output_dir (str, optional): Destination directory for renamed files
            inplace (bool, optional): Rename files in the same directory. Overrides output_dir.
            extension_filter (List[str], optional): List of file extensions to rename

        Returns:
            List[str]: Paths of renamed files
        """
        
        renamed_files_count = 0
        # Explicit rename map takes highest priority
        if rename_map:
            for old_path, new_path in rename_map:
                if extension_filter:      
                    if os.path.splitext(old_path)[1].lower() not in extension_filter:
                        continue
                    if os.path.splitext(new_path)[1].lower() not in extension_filter:
                        continue
                
                if os.path.exists(old_path):
                    if (os.path.exists(new_path)) and (not overwrite):
                        warnings.warn(f"there already exists a file named {os.path.basename(new_path)} " + \
                                            "in the destination. No overwrite permission given. " + \
                                            "If you want to overwrite, set overwrite=True")
                        return 0
                    
                    os.makedirs(os.path.dirname(new_path), exist_ok=True)
                    shutil.copy2(old_path, new_path)
                    renamed_files_count += 1
                else:
                    raise FileNotFoundError("{old_path} does not exist")
            
            return renamed_files_count
        
        
        # Input validation
        if  (input_dir is None) or (not os.path.isdir(input_dir)):
            raise ValueError(f"no valid files source provided")

        # Determine output directory
        if inplace:
            output_dir = input_dir
        elif output_dir is None:
            warnings.warn("no valid output_dir provided. If you wish to rename in the same dir, set inplace=True")
            return 0

        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)

        # Get list of files
        all_files = AudioMan.get_sorted_files(input_dir)
        
        # Filter files by extension if provided
        if extension_filter:
            ext_filtered_files = []
            for f in all_files:
                for ext in extension_filter:
                    if (not ext) or ext[0] != '.':
                        raise ValueError("invalid extension given. Make sure the extensions start with a '.'. eg: .wav")
                    
                    if os.path.splitext(f)[1].lower().endswith(ext.lower()):
                        ext_filtered_files.append(f)
            
            all_files = ext_filtered_files
            

        if not all_files:
            warnings.warn(f"no files in {input_dir}, with the given requirements, found")
            return 0
        

        # Prepare for numbered renaming
        if file_unq_ids:
            if len(all_files) != len(file_unq_ids):
                raise ValueError("number of files in the input directory do not match with the file_unq_ids")
            file_unq_ids_iter = iter(file_unq_ids)
            current_number = next(file_unq_ids_iter)
        else:
            current_number = start_number
            

        for filename in all_files:
            # Get file extension
            file_ext = os.path.splitext(filename)[1]
            
            
            
            # Construct new filename
            new_filename = f"{output_prefix}{delim}{current_number}{delim}{output_suffix}{file_ext}"

            # Source and destination paths
            src_path = os.path.join(input_dir, filename)
            dst_path = os.path.join(output_dir, new_filename)

            if os.path.exists(dst_path) and (not overwrite):
                warnings.warn(f"there already exists a file named {os.path.basename(dst_path)} " + \
                            "in the destination. No overwrite permission given. " + \
                            "If you want to overwrite, set overwrite=True")
                return 0
            
            if src_path == dst_path:
                continue
                
            # Copy or move file
            shutil.copy2(src_path, dst_path)
            renamed_files_count += 1

            # Set next id or number
            if file_unq_ids:
                current_number = next(file_unq_ids_iter, None)
            else:
                current_number += jump_by
                
        return renamed_files_count
'''