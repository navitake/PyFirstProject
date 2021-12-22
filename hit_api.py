import requests
import pprint

url = "http://localhost:8080"
imageURI = r"input.png"
openImage = {'upload_file': open(imageURI,"rb")}
print(openImage)

# pyaload = {"image": imageBinary}
result = requests.post(url, files=openImage)

print(result.text)
pprint.pprint(result.json(),depth=2,compact=True)
