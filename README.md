# Panlex-Lexicon-Extractor
# Usage
Download the required [file](https://drive.google.com/file/d/1tyACWPYrOQJ4m20dTjDPWtpX1XGYWtyf/view?usp=sharing) of Panlex language information. Put it under the folder of 'data'

Download the preprocessed SQLite file of Panlex database [here](), uncompress and put it under the folder of 'database'

```
python panlex_bilingual_extract.py --source_language=spa --target_language=eng --output_directory=lexicons
```