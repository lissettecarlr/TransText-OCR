import yaml

class Config():
    def __init__(self) -> None:
        with open('./config/cfg.yaml', 'r',encoding="utf-8") as file:
            self.config = yaml.safe_load(file)

        self.language_list = self.config['languageList']
        self.default_language = self.config['defaultLanguage']
        self.local_ocr_engine_path = self.config['localOcrEnginePath']
        self.temp_files_path = self.config['tempFilesPath']
        self.ocr_interval = self.config['ocrInterval']
        self.img_similarity_score = self.config['imgSimilarityScore']
        self.translate_engine_list = self.config['translateEngineList']
        self.translate_to_language = self.config['translateTolanguage']
        self.translate_from_language = self.config['translateFromlanguage']
        self.ocr_break_line = self.config['ocrBreakLine']
