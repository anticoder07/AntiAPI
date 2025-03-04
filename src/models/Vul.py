class Vul:
    def __init__(self, vul_id, api_id, payload, vul_type, vul_status, regex_fix):
        self.vul_id = vul_id
        self.api_id = api_id
        self.payload = payload
        self.vul_type = vul_type
        self.vul_status = vul_status
        self.regex_fix = regex_fix
