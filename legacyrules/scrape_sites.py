import requests
from bs4 import BeautifulSoup
import urllib.parse
import os

def get_video_urls(soup, base_url):
    video_urls = set()
    
    # 1. Check <video> tags
    for video in soup.find_all('video'):
        if video.get('src'):
            video_urls.add(urllib.parse.urljoin(base_url, video.get('src')))
        for source in video.find_all('source'):
            if source.get('src'):
                video_urls.add(urllib.parse.urljoin(base_url, source.get('src')))
                
    # 2. Check <iframe> tags (YouTube, Vimeo, etc.)
    video_platforms = ['youtube.com', 'youtu.be', 'vimeo.com', 'dailymotion.com', 'player.vimeo.com', 'www.youtube-nocookie.com']
    for iframe in soup.find_all('iframe'):
        src = iframe.get('src')
        if src:
            # Normalize protocol-relative URLs
            if src.startswith('//'):
                src = 'https:' + src
            if any(platform in src for platform in video_platforms):
                video_urls.add(urllib.parse.urljoin(base_url, src))
                
    # 3. Check <a> tags that look like direct video links
    video_extensions = ('.mp4', '.webm', '.ogg', '.mov')
    for a in soup.find_all('a', href=True):
        href = a['href']
        if href.lower().split('?')[0].endswith(video_extensions):
            video_urls.add(urllib.parse.urljoin(base_url, href))
            
    return list(video_urls)

def main():
    sites_file = 'sites'
    if not os.path.exists(sites_file):
        # Check parent directory if not found in current
        sites_file = os.path.join('..', 'sites')
        if not os.path.exists(sites_file):
            print("Error: 'sites' file not found.")
            return

    try:
        with open(sites_file, 'r') as f:
            urls = [line.strip() for line in f if line.strip()]
    except Exception as e:
        print(f"Error reading sites file: {e}")
        return

    for url in urls:
        print(f"\n{'='*80}")
        print(f"URL: {url}")
        print(f"{'='*80}")
        
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract video URLs
            videos = get_video_urls(soup, url)
            
            print("\n[EMBEDDED VIDEOS]")
            if videos:
                for v_url in videos:
                    print(f"  - {v_url}")
            else:
                print("  (None found)")
                
            # Extract text
            # We strip script and style elements
            for script_or_style in soup(["script", "style"]):
                script_or_style.decompose()

            text = soup.get_text(separator=' ', strip=True)
            
            print("\n[PAGE TEXT CONTENT]")
            # Print a snippet or all text? Let's print the first 1000 chars for brevity in output
            # but the logic is there to handle the full text.
            print(text[:1000] + "..." if len(text) > 1000 else text)
            
        except Exception as e:
            print(f"FAILED to process {url}: {e}")

if __name__ == "__main__":
    main()
