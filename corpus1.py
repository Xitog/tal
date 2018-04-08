#===============================================================================
# Download notice from HAL
# Author : Damien Gouteux
# Last modified : 8 april 2018
#===============================================================================

#-------------------------------------------------------------------------------
# Import
#-------------------------------------------------------------------------------

import urllib.request
import urllib.parse
import json

#-------------------------------------------------------------------------------
# Main code
#-------------------------------------------------------------------------------

base_request = "https://api.archives-ouvertes.fr/search/?wt=json&fl=docid,domain_s,authFullName_s,docType_s,title_s,language_s,modifiedDateY_i&fq=language_s:fr&indent=true&sort=docid%20desc&rows=100&cursorMark="
nb = 310 #1
request = base_request + 'AoFXtZUG' #'*'
try:
    while nb < 3100:
        print(f'call {nb:04d}', request)
        response = urllib.request.urlopen(request)
        raw_content = response.read()
        content = json.loads(raw_content)
        del raw_content
        if 'nextCursorMark' not in content:
            print('nextCursorMark not found!')
            if 'error' in content:
                print(content['error'])
            #[print(key) for key in content]
            break
        print(f'answer {nb:04d}', content['nextCursorMark'], len(content['response']['docs']))
        request = base_request + urllib.parse.quote(content['nextCursorMark'])
        output_file = open(f'output_{nb:04d}.txt', mode='w', encoding='utf8')
        json.dump(content, output_file, indent=4, ensure_ascii=False)
        output_file.close()
        nb += 1
except urllib.error.URLError as e:
    print('Impossible to reach the server:')
    print(f'    {e.reason}')
