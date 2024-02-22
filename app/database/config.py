from database import db

class Config():
    """config 테이블을 핸들링 하기 위한 클래스
    """

    db = None

    def __init__(self, db):
        self.db = db

    def get_config(self, config_name):
        """config_name 에 해당하는 설정을 구한다.

        Args:
            config_name (string): 설정명 (config 테이블의 key 값)

        Returns:
            string: config 테이블의 value 값
        """
        df = self.db.select(f"select * from config where key='{config_name}'")
        if self.is_valid(df):
            return df[df['key'] == config_name]['value'].item()
        else:
            return ''

    def set_config(self, config_name, str_value):
        """config_name 에 해당하는 설정값을 저장한다.

        Args:
            config_name (string): 설정명 (config 테이블의 key 값)
            str_value (string): 설정값 (config 테이블의 value 값) 
        """
        sql = f"update config set value='{str_value}' where key='{config_name}'"
        self.db.execute(sql)

    def is_valid(self, df):
        if not isinstance(df, type(None)) and (len(df) > 0):
            return True
        else:
            return False

