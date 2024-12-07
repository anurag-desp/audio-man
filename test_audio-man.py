from AudioMan import AudioMan

# # change extensions
# renamed_count = AudioMan.total_rename(
#     input_dir='audio',
#     delim='_',
#     # output_prefix='',
#     output_suffix='',
#     nomenclature='n',
#     start_number=2,
#     # overwrite=True,
#     # extension_filter = ['.wav', '.mp3']
#     # start_number=10,
# )
# print(renamed_count)

# split_count = AudioMan.split_audio_file(
#     input_path='audio/suzume.mp3',
#     segment_duration_secs=30,
#     output_dir='audio/suzume_segments',
#     keep_output_format=True,
#     # output_prefix=None,
#     # output_suffix=None,
#     delim='-',
#     start_number=1,
#     jump_by=1,
#     keep_consistent_num_length=True,
#     drop_last=True
# )
# print(split_count)

# changed_ext_count = AudioMan.change_extension(
#     input_dir='audio/suzume_segments',
#     from_ext='.wav',
#     to_ext='.mp3',
#     make_copy=False,
#     overwrite=True
# )
# print(changed_ext_count)





split_count, split_seg_count = AudioMan.split_audio_files(
    input_dir  = 'audio',
    output_dir = 'audio/output_segments',
    segment_duration_secs = 5, 
    keep_output_format = True,
    # extension_filter = ['.wav'],
    output_format = 'wav',
    nomenclature = 'on',
    # output_prefix = "ai",
    # output_suffix = "anurag",
    delim = "_",
    keep_numbering_local = True,
    start_number = 1,
    jump_by = 1,
    keep_consistent_num_length = False,
    drop_last = True,
    overwrite=True
)

print(split_count)
print(split_seg_count)