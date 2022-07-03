# --// Imports

import re
import os
import sys
import shutil
import requests

# --// Validate

class _:
    class patterns:
        image = '<img src="([^"]+)"'
        link  = '<a href=\"([^"]+)"'
        src   = '<source src=\"([^"]+)"'
        style = '<style href=\"([^"]+)"'

        src_r = 'src=\"([^"]+)"'
        ref_r = 'href=\"([^"]+)"'

        all = [image, link, src]

if not os.path.exists("./sites.txt"):
    print("File 'sites.txt' missing!")

    sys.exit()

# --// Parse

out_dir = sys.argv[1]

full = " ".join(sys.argv)

if "-h" in full or "--help" in full:
    print("""

OSINT - RoosterQMonee

--// Commands

python OSINT [-h][-gi][--getimages][-gs][--getsource]
             [-grs][--getrawsources][-p][--print][-b]
             [--build][-d][--download][--help]

--// Usage

    50/50 chance these work, I didnt really plan for this a whole lot

    [-h][--help]            Display help command 
    [-gi][--getimages]      Download images from sites                   ( default: False )
    [-gs][--getsources]     Download source files (.js, .css...)         ( default: False )
    [-grs][--getrawsources] Download every src tag                       ( default: False )
    [-p][--print]           Print final tree on finish                   ( default: True )
    [-b][--build]           Attempt to recreate site with website source ( default: False )
    [-d][--download]        Actually download site                       ( default: False )

    """)

    sys.exit()

get_images = False
get_sources = False
get_rsources = False
build = False
print_data = True
download = True

if "-gi" in full:             get_images   = True
if "--getimages" in full:     get_images   = True
if "-gs" in full:             get_sources  = True
if "--getsources" in full:    get_sources  = True
if "--getrawsources" in full: get_rsources = True
if "-grs" in full:            get_rsources = True
if "-p" in full:              print_data   = True
if "--print" in full:         print_data   = True
if "-d" in full:              download     = True; get_rsources = True; get_sources = True; get_images = True
if "-b" in full:              build        = True; get_rsources = True; get_sources = True; get_images = True
if "--download" in full:      download     = True; get_rsources = True; get_sources = True; get_images = True
if "--build" in full:         build        = True; get_rsources = True; get_sources = True; get_images = True

# --// Data

with open("sites.txt", "r") as dat:
    data = " ".join([char.replace("\n", "") for char in dat.readlines()]).split()

tags = _.patterns

url_data     = ""
sites        = []

# --// Create data tree

try:
    os.mkdir(out_dir)
    os.mkdir(f"./{out_dir}/images")
    os.mkdir(f"./{out_dir}/hrefs")
    os.mkdir(f"./{out_dir}/sources")
    os.mkdir(f"./{out_dir}/raw_sources")

except:
    try:
        shutil.rmtree(out_dir)

    except Exception as e:
        print('Failed to delete %s. Reason: %s' % ("scrape", e))
        
    os.mkdir(out_dir)
    os.mkdir(f"./{out_dir}/images")
    os.mkdir(f"./{out_dir}/hrefs")
    os.mkdir(f"./{out_dir}/sources")
    os.mkdir(f"./{out_dir}/raw_sources")

# --// Search

if download:
    for site in data:
        base = site.replace("www.", "")
        
        print(f"[+] Building: {base}")
        print()
        
        os.mkdir(f"./{out_dir}/images/" + base.split("https://")[1].split(".")[0])
        os.mkdir(f"./{out_dir}/sources/" + base.split("https://")[1].split(".")[0])
        os.mkdir(f"./{out_dir}/raw_sources/" + base.split("https://")[1].split(".")[0])

        response = requests.get(site + url_data)

        status   = response.status_code
        text     = response.text
        headers  = response.headers

        if status == 200:
            images   = re.findall(tags.image, text)
            hrefs    = re.findall(tags.link,  text)
            sources  = re.findall(tags.src,   text)

            rhrefs   = re.findall(tags.ref_r, text)
            rsources = re.findall(tags.src_r, text)

            if get_images:
                for index, image in enumerate(images):
                    try:
                        if "https://" in image or "http://" in image:
                            res  = requests.get(image)
                            fype = res.headers.get('content-type').split("/")[1]

                            sname = base.split("https://")[1].split(".")[0]
                            with open(f"./{out_dir}/images/{sname}/image-{str(index)}.{fype}", "wb") as file:
                                file.write(res.content)

                    except Exception as e:
                        print(f"[!] Search error: {e}, Continuing...")

            if get_sources:
                for index, image in enumerate(sources):
                    try:
                        if "https://" in image or "http://" in image:
                            res  = requests.get(image)
                            fype = res.headers.get('content-type').split("/")[1]

                            sname = base.split("https://")[1].split(".")[0]
                            url = image.split("/")[-1]
                            with open(f"./{out_dir}/sources/{sname}/{url}.{fype}", "wb") as file:
                                file.write(res.content)

                    except Exception as e:
                        print(f"[!] Search error: {e}, Continuing...")

            if get_rsources:
                for index, image in enumerate(rsources):
                    try:
                        if "https://" in image or "http://" in image:
                            res  = requests.get(image)
                            fype = res.headers.get('content-type').split("/")[1]

                            sname = base.split("https://")[1].split(".")[0]
                            url = image.split("/")[-1]
                            with open(f"./{out_dir}/raw_sources/{sname}/{url}.{fype}", "wb") as file:
                                file.write(res.content)

                    except Exception as e:
                        print(f"[!] Search error: {e}, Continuing...")

                for index, image in enumerate(rhrefs):
                    try:
                        if "https://" in image or "http://" in image:
                            res  = requests.get(image)
                            fype = res.headers.get('content-type').split("/")[1]

                            sname = base.split("https://")[1].split(".")[0]
                            url = image.split("/")[-1]
                            with open(f"./{out_dir}/raw_sources/{sname}/{url}.{fype}", "wb") as file:
                                file.write(res.content)

                    except Exception as e:
                        print(f"[!] Search error: {e}, Continuing...")
            
            if build:
                os.mkdir(f"./{out_dir}/{sname}")
                os.mkdir(f"./{out_dir}/{sname}/build")

                with open(f"./{out_dir}/{sname}/build/index.html", mode="w", encoding="UTF-8") as build:
                    build.write(text)

                for file in os.listdir(f"./{out_dir}/raw_sources/{sname}"):
                    nf = file.replace(".javascript", "")
                    shutil.copyfile(f"./{out_dir}/raw_sources/{sname}/" + file, f"./{out_dir}/{sname}/build/{nf}")

                for file in os.listdir(f"./{out_dir}/images/{sname}"):
                    nf = file.replace(".javascript", "")
                    shutil.copyfile(f"./{out_dir}/images/{sname}/" + file, f"./{out_dir}/{sname}/build/{nf}")

                print(f"[+] Built '{base}' with './{out_dir}/raw_sources'")

            sites.      append({"status":"valid", "url":site, "images":images, "links":hrefs, "sources":sources, "raw_sources":rsources, "raw_links":rhrefs})

        else:
            sites.      append({"status":"invalid", "url":site, "images":[], "links":[], "sources":[], "raw_sources":[], "raw_links":[]})

else:
    for site in data:
        base = site.replace("www.", "")
        print()
        print(f"[+] Building: {base}")

        os.mkdir(f"./{out_dir}/images/" + base.split("https://")[1].split(".")[-2])
        os.mkdir(f"./{out_dir}/sources/" + base.split("https://")[1].split(".")[-2])
        os.mkdir(f"./{out_dir}/raw_sources/" + base.split("https://")[1].split(".")[-2])

        response = requests.get(site + url_data)

        status   = response.status_code
        text     = response.text
        headers  = response.headers

        if status == 200:
            images   = re.findall(tags.image, text)
            hrefs    = re.findall(tags.link,  text)
            sources  = re.findall(tags.src,   text)

            rhrefs   = re.findall(tags.ref_r, text)
            rsources = re.findall(tags.src_r, text)

            sites.      append({"status":"valid", "url":site, "images":images, "links":hrefs, "sources":sources, "raw_sources":rsources, "raw_links":rhrefs})

        else:
            sites.      append({"status":"invalid", "url":site, "images":[], "links":[], "sources":[], "raw_sources":[], "raw_links":[]})


print("\n")

with open(f"./{out_dir}/data_tree.txt", mode="w", encoding="UTF-8") as out:
    for site in sites:
        if site["status"] == "valid":
            uri = site["url"]
            out.write(f"[*] -- [ {uri} ]\n")
        
            out.write("├─ Images\n")
            for image in site["images"]:
                name = image.split("/")[-1]
                out.write(f"│  ├─ {name}\n")

            out.write("│\n")

            out.write("├─ Links\n")
            for url in site["links"]:
                out.write(f"│  ├─ {url}\n")

            out.write("│\n")

            out.write("├─ Sources\n")
            for url in site["sources"]:
                out.write(f"│  ├─ {url}\n")

            out.write("│\n")
            out.write("│\n├─// Raw Data\n│\n")
            out.write("│\n")

            out.write("├─ Raw Sources\n")
            for url in site["raw_sources"]:
                out.write(f"│  ├─ {url}\n")

            out.write("│\n")

            out.write("├─ Raw links\n")
            for url in site["raw_links"]:
                out.write(f"│  ├─ {url}\n")

if print_data:
    for site in sites:
        if site["status"] == "valid":
            uri = site["url"]
            print(f"[*] -- [ {uri} ]")
        
            print("├─ Images")
            for image in site["images"]:
                name = image.split("/")[-1]
                print(f"│  ├─ {name}")

            print("│")

            print("├─ Links")
            for url in site["links"]:
                print(f"│  ├─ {url}")

            print("│")

            print("├─ Sources")
            for url in site["sources"]:
                print(f"│  ├─ {url}")

            print("│")
            print("│\n├─// Raw Data\n│")
            print("│")

            print("├─ Raw Sources")
            for url in site["raw_sources"]:
                print(f"│  ├─ {url}")

            print("│")

            print("├─ Raw links")
            for url in site["raw_links"]:
                print(f"│  ├─ {url}")

        print()

    print(f"[=] Finished, saved to {out_dir}")

else:
    print(f"[=] Finished, saved to {out_dir}")
