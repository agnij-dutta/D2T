from youtube_transcript_api import YouTubeTranscriptApi
from urllib.parse import urlparse, parse_qs

class VideoService:
    def get_video_id(self, url):
        """Extract video ID from YouTube URL"""
        query = urlparse(url)
        if query.hostname == 'youtu.be':
            return query.path[1:]
        if query.hostname in ('www.youtube.com', 'youtube.com'):
            if query.path == '/watch':
                return parse_qs(query.query)['v'][0]
        raise ValueError('Invalid YouTube URL')

    def get_transcript(self, url):
        """Get video transcript and save it"""
        video_id = self.get_video_id(url)
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
        transcript_text = ' '.join([t['text'] for t in transcript_list])
        
        # Save transcript to file
        with open('transcript.txt', 'w', encoding='utf-8') as f:
            f.write(transcript_text)
        print(f"[DEBUG] Saved transcript to transcript.txt")
        
        return transcript_text