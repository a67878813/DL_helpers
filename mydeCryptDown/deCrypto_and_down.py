
import os 
import re
import requests
import os,uuid
from Crypto.Cipher import AES
import subprocess


class myDecrypoAndDown:
    """
    加密m3u8下载器
    使用方法
    myDecrypoAndDown(m3u8url, outname).downloadMP4()

    """
    def __init__(self,_m3u8_url,_out_name):
        self.m3u8_url =_m3u8_url
        self.out_name = _out_name
        self.down_dir= "Y:\\m3u8\\"
        self.ffmpeg_dir="\"D:\\Program Files\\ffmpeg\\ffmpeg.exe\""
        self.ts_list =[]
        self.m3u8content =""
        self.crypt = False

        self._file2 =self.down_dir+"__temp__.txt"
        self.ts_temp_file_list =[]
    
    def get_m3u8_content(self):
        res = requests.get(self.m3u8_url)
        self.m3u8content =  res.content.decode('utf-8')


    def is_crpted(self):
        res =  re.findall('#EXT-X-KEY:METHOD=(.*?),', self.m3u8content)
        if len(res)>=1:
            return True
        else:
            return False
    def get_keys(self):
        key_url = re.findall('(?<=").*?(?=")', self.m3u8content)[0]
        res = requests.get(key_url)
        self.key = res.content
        print(" Crypt key: ",self.key.hex())
        iv=re.findall('IV=(.*?)\n',self.m3u8content)[0]
        print(" IV: ",iv)
        iv=iv.replace('0x','')
        self.iv=bytes.fromhex(iv)
        self.cryptor = AES.new(self.key, AES.MODE_CBC, self.iv)
    def get_ts_lists(self):
        pay_list = self.m3u8content.split('\n')
        ts_list = []
        for i in pay_list:
            if i != "":
                if i[0] != '#':
                    ts_list.append(i)
        self.ts_list = ts_list

    def down_crypt_ts(self):
        ffmpeg_txt_l =[]

        for i , p in enumerate(self.ts_list):
            #base_url + p
            ts_url = p
            res = requests.get(ts_url)
            file_name = str(i).rjust(4,'0') +'.ts'
            _file = self.down_dir+"__temp__" +file_name
            self.ts_temp_file_list.append(_file)
            ffmpeg_txt_l.append("file '__temp__" +file_name +"'")

            with open(_file,'wb') as f:
                f.write(self.cryptor.decrypt(res.content))
        with open(self._file2,'w') as f:
            f.write('\n'.join(ffmpeg_txt_l))

    def ts2mp4(self):
        cmd = self.ffmpeg_dir +" -loglevel quiet -f concat  -safe 0  -i __temp__.txt -c copy output.mp4"
        print(cmd)
        a =subprocess.check_output(cmd, shell=True, cwd=self.down_dir)
    
    def rename_out_file(self):
        src1= self.down_dir + "output.mp4"
        dst1 = self.down_dir +self.out_name +".mp4"
        os.rename(src=src1,dst=dst1)
    def delete_temp_files(self):
        os.remove(self._file2)
        for i in self.ts_temp_file_list:
            os.remove(i)
    def downloadMP4(self):

        self.get_m3u8_content()
        if self.is_crpted():
            self.get_ts_lists()
            self.get_keys()
            self.down_crypt_ts()
            self.ts2mp4()
            self.rename_out_file()
            self.delete_temp_files()



