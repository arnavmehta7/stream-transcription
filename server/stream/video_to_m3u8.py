# ffmpeg -i ~/Downloads/samples/vid.mp4 -profile:v baseline -level 3.0 -s 640x360 -start_number 0 -hls_time 10 -hls_list_size 0 -f hls output.m3u8
import ffmpeg

def video_to_m3u8(video_path: str, output_path: str):
    assert output_path.endswith(".m3u8"), "Output path must have .m3u8 extension"
    (
        ffmpeg
        .input(video_path)
        .output(
            output_path,
            format="hls",
            start_number=0,
            hls_time=10,
            hls_list_size=0,
        )
        .run(overwrite_output=True)
    )
