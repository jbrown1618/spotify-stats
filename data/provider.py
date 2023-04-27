class DataProvider:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DataProvider, cls).__new__(cls)

        return cls._instance
    