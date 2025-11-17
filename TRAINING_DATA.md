# Training Data Sources

Comprehensive list of sources for training the Music Theory ML Model.

## 🎵 Music Theory Datasets

### 1. **iReal Pro Chord Progressions**
- **Source**: iReal Pro Forum, user-shared playlists
- **Content**: 10,000+ jazz standards, pop songs, latin, blues
- **Format**: iReal Pro format (can be parsed)
- **Access**: https://irealpro.com/ireal-pro-forums/
- **Use Case**: Chord progression training, style-specific models

### 2. **Hooktheory Database**
- **Source**: Hooktheory TheoryTab
- **Content**: 40,000+ analyzed songs with chords and melodies
- **Format**: Web scraping or API (requires subscription)
- **Access**: https://www.hooktheory.com/theorytab
- **Use Case**: Progression analysis, melody-harmony relationships

### 3. **WikiFonia / Fake Book**
- **Source**: Archive.org (WikiFonia was taken down but archived)
- **Content**: 6,500+ lead sheets in MusicXML
- **Format**: MusicXML
- **Access**: https://archive.org/details/wikifonia
- **Use Case**: Melody and chord training

### 4. **The Jazz Real Book**
- **Source**: Various digitized versions
- **Content**: 400+ jazz standards
- **Format**: PDF, some MusicXML conversions
- **Use Case**: Jazz progression patterns, ii-V-I analysis

### 5. **Ultimate Guitar Tabs**
- **Source**: Ultimate-Guitar.com
- **Content**: 1M+ guitar tabs with chords
- **Format**: Web scraping (respect robots.txt)
- **Access**: https://www.ultimate-guitar.com
- **Use Case**: Rock/pop progressions, guitar-specific voicings

## 🎹 MIDI Datasets

### 6. **Lakh MIDI Dataset**
- **Source**: Colin Raffel (Columbia University)
- **Content**: 176,581 MIDI files
- **Format**: MIDI
- **Access**: https://colinraffel.com/projects/lmd/
- **Use Case**: Large-scale pattern learning, melody extraction

### 7. **Classical Piano MIDI**
- **Source**: Maestro Dataset (Google Magenta)
- **Content**: 1,200+ classical piano performances
- **Format**: MIDI + Audio
- **Access**: https://magenta.tensorflow.org/datasets/maestro
- **Use Case**: Classical music analysis, voice leading

### 8. **Free MIDI Files**
- **Source**: Various (FreeMidi.org, BitMidi.com)
- **Content**: 100,000+ MIDI files
- **Format**: MIDI
- **Use Case**: Diverse style training

## 📊 Academic Datasets

### 9. **McGill Billboard Dataset**
- **Source**: McGill University
- **Content**: 1,000 pop songs from Billboard charts
- **Format**: Text files with chord annotations
- **Access**: https://ddmal.music.mcgill.ca/research/The_McGill_Billboard_Project_(Chord_Analysis_Dataset)/
- **Use Case**: Pop music analysis, hit song patterns

### 10. **Jazz Audio-Aligned Dataset**
- **Source**: Various jazz researchers
- **Content**: Annotated jazz recordings
- **Format**: JSON/XML with timing
- **Use Case**: Jazz-specific training

### 11. **Million Song Dataset**
- **Source**: Columbia University / The Echo Nest
- **Content**: 1M songs with audio features
- **Format**: HDF5
- **Access**: http://millionsongdataset.com/
- **Use Case**: Large-scale analysis (no MIDI but has features)

## 🎸 Guitar-Specific Sources

### 12. **Transcription Databases**
- **Guitar Tabs Universe**: Community transcriptions
- **Songsterr**: Interactive tabs (requires parsing)
- **Tab collections**: Various artists' official tablature books

### 13. **Blues Lick Collections**
- **Blues You Can Use** by John Ganapes
- **BB King Master Class**: Transcribed solos
- **Blues Guitar Inside Out** by Richard Gilewitz
- Format: Need manual digitization from books/videos

### 14. **Rock Guitar Archives**
- **Led Zeppelin Complete** (official transcriptions)
- **Jimi Hendrix Complete Scores**
- **Eric Clapton Complete Clapton**
- Format: Guitar tablature books (need digitization)

## 🔧 Music21 Corpus

### 15. **music21 Built-in Corpus**
- **Source**: MIT's music21 library
- **Content**: 1,000+ classical pieces, Bach chorales, folk songs
- **Format**: MusicXML, ABC, MIDI
- **Access**: Built into music21 Python library
```python
from music21 import corpus
corpus.search('bach')
```

## 🌐 APIs and Services

### 16. **Spotify API**
- **Content**: Audio features, key, tempo, time signature
- **Access**: https://developer.spotify.com/documentation/web-api/
- **Use Case**: Style classification, audio feature analysis

### 17. **MusicBrainz**
- **Content**: Metadata, relationships between artists/songs
- **Access**: https://musicbrainz.org/doc/MusicBrainz_API
- **Use Case**: Dataset curation, artist/genre tagging

### 18. **AcousticBrainz**
- **Content**: Audio analysis data
- **Access**: https://acousticbrainz.org/
- **Use Case**: Audio feature extraction

## 📝 Text-Based Sources

### 19. **Chord Progression Forums**
- Reddit r/musictheory progressions
- Ultimate-Guitar forums
- Jazz Standards progression lists

### 20. **YouTube Transcriptions**
- Channels with transcribed solos
- Tutorial channels with lick breakdowns
- Community annotations

## 🎓 Academic Papers with Datasets

### 21. **Automatic Chord Recognition Papers**
- MIREX (Music Information Retrieval) datasets
- Various academic chord datasets

### 22. **Jazz Solo Transcriptions**
- Weimar Jazz Database
- Charlie Parker Omnibook digitized

## 🛠️ Data Generation Tools

### 23. **Musescore Library**
- **Content**: User-uploaded scores
- **Format**: MuseScore, can export to MusicXML
- **Access**: https://musescore.com/
- **Use Case**: Full score analysis

### 24. **Flat.io**
- **Content**: Sheet music platform
- **Format**: Can export various formats
- **Access**: https://flat.io/

## 📚 Books to Digitize

### Blues Guitar (1960s-1980s)
1. **"Blues You Can Use"** - John Ganapes
2. **"Blues Guitar Inside and Out"** - Richard Gilewitz
3. **"The Blues Scale"** - Dan Greenblatt
4. **"Chicago Blues Guitar"** - Dave Rubin
5. **"Texas Blues Guitar"** - Robert Calva

### Rock Guitar
1. **"Led Zeppelin Complete"** - Official transcriptions
2. **"Jimi Hendrix - Blues"** - Transcribed solos
3. **"Cream Complete"** - Eric Clapton transcriptions
4. **"The Rolling Stones Complete"**
5. **"Deep Purple Authentic Guitar-Tab"**

## 💾 Preprocessing Pipeline

### Recommended Processing Steps:

```python
# 1. Load from source
from music21 import converter
score = converter.parse('song.mid')

# 2. Extract chords
chords = score.flat.getElementsByClass('Chord')

# 3. Analyze key
key = score.analyze('key')

# 4. Convert to our format
from src.theory import Note, Chord, ChordProgression, Scale
progressions = []
for chord in chords:
    # Convert to our Chord class
    ...
```

## 📊 Recommended Dataset Sizes

For effective training:
- **Minimum**: 1,000 progressions
- **Good**: 10,000 progressions
- **Excellent**: 100,000+ progressions

By style:
- Jazz: 5,000+ progressions (more complex)
- Pop: 10,000+ progressions (more examples needed)
- Classical: 3,000+ pieces (already complex)
- Blues: 2,000+ progressions (patterns repeat)
- Rock: 5,000+ progressions

## 🚀 Quick Start Scripts

### Script 1: Load from music21 corpus
```python
from music21 import corpus, converter
from src.theory import ChordProgression, Scale, Note

bach_chorales = corpus.search('bach', 'composer')
progressions = []

for work in bach_chorales[:100]:
    score = work.parse()
    # Extract chords and convert to our format
    # ... (see data loading utilities)
```

### Script 2: Parse iReal Pro
```python
import pyrealpro  # hypothetical library

songs = pyrealpro.load('jazz_standards.html')
for song in songs:
    chords = song.get_chords()
    # Convert to our format
```

### Script 3: Generate synthetic data
```python
from src.intelligence.statistical_analyzer import StatisticalProgressionAnalyzer

analyzer = StatisticalProgressionAnalyzer()
# Generate 1000 synthetic progressions based on learned patterns
synthetic = [
    analyzer.generate_likely_progression(
        start_chord, scale, length=4
    )
    for _ in range(1000)
]
```

## ⚖️ Legal Considerations

- **Public Domain**: Pre-1928 works in US
- **Fair Use**: Educational purposes, research
- **Creative Commons**: Many user-uploaded scores
- **Respect Copyright**: Don't distribute copyrighted transcriptions
- **APIs**: Follow terms of service

## 🎯 Recommended Starting Point

1. **Start with**: music21 corpus (free, legal, ready to use)
2. **Add**: McGill Billboard dataset (pop music)
3. **Expand**: Lakh MIDI dataset (variety)
4. **Specialize**: iReal Pro for jazz, Ultimate Guitar for rock
5. **Generate**: Use statistical analyzer to create synthetic data

## 📝 Data Format Standards

Store processed data as:
```json
{
  "progression": ["C", "Am", "F", "G"],
  "key": "C major",
  "style": "pop",
  "source": "McGill Billboard",
  "song_id": "1234",
  "roman_numerals": ["I", "vi", "IV", "V"]
}
```

## 🔄 Continuous Data Collection

Set up pipelines to:
1. Monitor new uploads to MuseScore/Flat
2. Scrape new Ultimate Guitar tabs (ethically)
3. Collect user-contributed progressions
4. Record progressions from your own app usage

## 🎼 Example: Loading Your First Dataset

```bash
# Create data loading script
cd /home/user/music-theory-llm
python scripts/load_training_data.py --source music21 --limit 1000 --output data/processed/
```

See `data/data_loaders.py` for complete implementation.
