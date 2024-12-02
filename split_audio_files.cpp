#include <iostream>
#include <cmath>
#include <filesystem>
#include <stdexcept>
#include <cstdlib>
#include <string>
#include <iomanip>
#include <sstream>

class AudioSplitter {
public:
    /**
     * Split an audio file into multiple files of a specified duration
     * 
     * @param inputFile Path to the input audio file
     * @param outputDirectory Directory where split files will be saved
     * @param segmentDuration Duration of each segment in seconds
     * @param outputPrefix Prefix for output file names (optional)
     * @throws std::runtime_error if FFmpeg command fails
     */
    static void splitAudioFile(
        const std::string& inputFile, 
        const std::string& outputDirectory, 
        double segmentDuration, 
        const std::string& outputPrefix = "segment_"
    ) {
        // Validate input file exists
        if (!std::filesystem::exists(inputFile)) {
            throw std::runtime_error("Input file does not exist: " + inputFile);
        }

        // Create output directory if it doesn't exist
        std::filesystem::create_directories(outputDirectory);

        // Construct FFmpeg command
        std::stringstream command;
        command << "ffmpeg -i \"" << inputFile << "\" "
                << "-f segment "
                << "-segment_time " << segmentDuration << " "
                << "-c copy "
                << "\"" << outputDirectory << "/" << outputPrefix << "%03d.mp3\"";

        // Execute FFmpeg command
        int result = std::system(command.str().c_str());

        // Check command execution result
        if (result != 0) {
            throw std::runtime_error("Failed to split audio file. FFmpeg command failed.");
        }
    }

    /**
     * Get total duration of an audio file using FFmpeg
     * 
     * @param inputFile Path to the input audio file
     * @return Total duration of the audio file in seconds
     * @throws std::runtime_error if duration cannot be retrieved
     */
    static double getAudioDuration(const std::string& inputFile) {
        // Construct FFmpeg command to get duration
        std::stringstream command;
        command << "ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 \"" 
                << inputFile << "\"";

        // Open pipe to capture command output
        FILE* pipe = popen(command.str().c_str(), "r");
        if (!pipe) {
            throw std::runtime_error("Could not open pipe to FFprobe");
        }

        // Read duration from output
        char buffer[128];
        std::string result;
        while (!feof(pipe)) {
            if (fgets(buffer, 128, pipe) != NULL)
                result += buffer;
        }
        pclose(pipe);

        // Convert to double
        try {
            return std::stod(result);
        } catch (const std::exception& e) {
            throw std::runtime_error("Failed to parse audio duration");
        }
    }

    /**
     * Calculate number of segments based on total duration and segment length
     * 
     * @param totalDuration Total audio file duration in seconds
     * @param segmentDuration Duration of each segment in seconds
     * @return Number of segments
     */
    static int calculateSegmentCount(double totalDuration, double segmentDuration) {
        return static_cast<int>(std::ceil(totalDuration / segmentDuration));
    }
};

// Example usage
int main() {
    try {
        std::string inputFile = "flirting_with_june.mp3";
        std::string outputDir = "output_segments";
        double segmentDuration = 60.0; // 60 seconds per segment

        // Get total audio duration
        double totalDuration = AudioSplitter::getAudioDuration(inputFile);
        std::cout << "Total audio duration: " << totalDuration << " seconds\n";

        // Calculate number of segments
        int segmentCount = AudioSplitter::calculateSegmentCount(totalDuration, segmentDuration);
        std::cout << "Will create " << segmentCount << " segments\n";

        // Split the audio file
        AudioSplitter::splitAudioFile(inputFile, outputDir, segmentDuration);

        std::cout << "Audio file split successfully!\n";
    }
    catch (const std::exception& e) {
        std::cerr << "Error: " << e.what() << std::endl;
        return 1;
    }

    return 0;
}