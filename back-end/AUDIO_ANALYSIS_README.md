# 🎵 Audio Analysis for Scam Detection

## Overview

This module provides AI-powered audio analysis capabilities for detecting potential scams in phone conversations. It uses OpenAI's Whisper API for audio transcription and GPT models for scam detection analysis.

## Features

- **Audio Transcription**: Automatically transcribes WAV audio files using OpenAI's Whisper API
- **Scam Detection**: Analyzes transcribed content for scam indicators using AI
- **Risk Assessment**: Provides risk levels (Low/Medium/High) with confidence scores
- **Vietnamese Language Support**: Optimized for Vietnamese language content
- **File Validation**: Ensures only WAV files under 25MB are processed
- **Temporary File Handling**: Secure temporary file management with automatic cleanup

## API Endpoint

### Audio Assessment

```http
POST /scam-detection/audio-assessment/
```

**Request:**
- Content-Type: `multipart/form-data`
- Body: `audio_file` (WAV file)

**Response:**
```json
{
  "transcript": "Transcribed audio content...",
  "analysis": "Detailed analysis of potential scam indicators...",
  "recommendation": "Specific actions user should take...",
  "risk_level": "HIGH|MEDIUM|LOW",
  "confidence": 85,
  "model_used": "gpt-4.1-mini",
  "audio_analyzed": true,
  "transcription_model": "whisper-1"
}
```

## Implementation Details

### 1. Audio Processing Pipeline

```
Audio File (WAV) → OpenAI Whisper API → Transcript → GPT Analysis → Risk Assessment
```

### 2. File Requirements

- **Format**: WAV audio files only
- **Size**: Maximum 25MB
- **Language**: Optimized for Vietnamese (configurable)

### 3. AI Models Used

- **Transcription**: OpenAI Whisper-1
- **Analysis**: GPT-4.1-mini (configurable)
- **Language**: Vietnamese (vi)

### 4. Risk Assessment Criteria

The AI analyzes transcripts for:
- OTP requests
- Banking information requests
- Threats or intimidation
- Prize notifications
- Suspicious links
- Personal information requests
- Urgency tactics

## Usage Examples

### Python Client

```python
import requests

def analyze_audio(audio_file_path):
    url = "http://localhost:8000/scam-detection/audio-assessment/"
    
    with open(audio_file_path, 'rb') as audio_file:
        files = {'audio_file': audio_file}
        response = requests.post(url, files=files)
        
    if response.status_code == 200:
        result = response.json()
        print(f"Risk Level: {result['risk_level']}")
        print(f"Confidence: {result['confidence']}%")
        print(f"Analysis: {result['analysis']}")
        return result
    else:
        print(f"Error: {response.text}")
        return None

# Usage
result = analyze_audio("conversation.wav")
```

### cURL Example

```bash
curl -X POST "http://localhost:8000/scam-detection/audio-assessment/" \
     -H "accept: application/json" \
     -H "Content-Type: multipart/form-data" \
     -F "audio_file=@conversation.wav"
```

## Error Handling

### Common Error Responses

```json
{
  "detail": "Only WAV audio files are supported"
}
```

```json
{
  "detail": "Audio file size must be less than 25MB"
}
```

```json
{
  "detail": "Audio analysis failed: [specific error message]"
}
```

## Configuration

### Environment Variables

```bash
OPENAI_API_KEY=your_openai_api_key_here
```

### Model Configuration

The service can be configured to use different models:

```python
# In llm_service.py
self.base_model = "gpt-4.1-mini"  # Change to other GPT models
self.whisper_model = "whisper-1"   # Change to other Whisper models
```

## Security Considerations

1. **File Validation**: Only WAV files are accepted
2. **Size Limits**: 25MB maximum file size
3. **Temporary Files**: Secure temporary file handling with automatic cleanup
4. **API Key Security**: OpenAI API key stored in environment variables
5. **Input Sanitization**: All inputs are validated and sanitized

## Performance

- **Transcription**: ~1-2 seconds per minute of audio (depending on quality)
- **Analysis**: ~2-5 seconds for typical conversation analysis
- **Total Processing**: ~3-7 seconds for complete analysis

## Limitations

1. **Audio Format**: Only WAV files supported
2. **File Size**: Maximum 25MB
3. **Language**: Optimized for Vietnamese, may work with other languages
4. **Audio Quality**: Better results with clear, high-quality audio
5. **API Dependencies**: Requires OpenAI API access and credits

## Testing

Use the provided test script:

```bash
python test_audio_analysis.py
```

## Troubleshooting

### Common Issues

1. **"Audio analysis not yet supported with Gemini"**
   - Switch to OpenAI provider in configuration

2. **"Only WAV audio files are supported"**
   - Convert audio to WAV format before uploading

3. **"Audio file size must be less than 25MB"**
   - Compress or split large audio files

4. **Transcription errors**
   - Check audio quality and OpenAI API key
   - Ensure audio contains speech (not just music/noise)

### Debug Mode

Enable detailed logging by setting log level to DEBUG in your logging configuration.

## Future Enhancements

1. **Multiple Audio Formats**: Support for MP3, M4A, etc.
2. **Real-time Analysis**: Streaming audio analysis
3. **Multi-language Support**: Better support for multiple languages
4. **Custom Models**: Integration with custom scam detection models
5. **Batch Processing**: Analyze multiple audio files simultaneously

## Dependencies

- `openai>=1.9.99.6`
- `fastapi`
- `python-multipart`
- `tempfile` (built-in)
- `pathlib` (built-in)

## Support

For issues or questions regarding audio analysis functionality, please refer to the main project documentation or create an issue in the project repository.
