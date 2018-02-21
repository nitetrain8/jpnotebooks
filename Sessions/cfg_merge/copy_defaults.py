import os, shutil
# copy script for v2.0
def copy_for_v2():
    fp = 'E:\\Users\\PBS Biotech\\Desktop\\1 Install RIO'
    out = "D:\\auto_hd_install\\default configs\\IC3405 Rev D"
    os.makedirs(out, exist_ok=True)
    for d in os.listdir(fp):
        ff = os.path.join(fp, d)
        if os.path.isdir(ff):
            for d2 in os.listdir(ff):
                ff2 = os.path.join(ff, d2)
                tdir = os.path.join(out, d)
                os.makedirs(tdir, exist_ok=True)
                if "cfg" in d2.lower() and os.path.isdir(ff2):  # CFG folder
                    for file in os.listdir(ff2):
                        ffp = os.path.join(ff2, file)
                        print("Copying %r to %r"%(file, tdir))
                        shutil.copy2(ffp, os.path.join(tdir, file))
                elif "LabVIEW Data" in d2:  # put contents in LV Data
                    for file in os.listdir(ff2):
                        if file[0] != "." and file[-4:] != ".lnk":
                            ffp = os.path.join(ff2, file)
                            print("Copying %r to %r"%(file, tdir))
                            shutil.copy2(ffp, os.path.join(tdir, file))

def copy_for_v3():
    # copy script for v3.0
    fp = 'E:\\Users\\PBS Biotech\\Desktop\\1 Install RIO'
    out = "D:\\auto_hd_install\\default configs\\IC3405 Rev E"
    os.makedirs(out, exist_ok=True)
    for d in os.listdir(fp):
        ff = os.path.join(fp, d)
        if os.path.isdir(ff):
            tdir = os.path.join(out, d)
            os.makedirs(tdir, exist_ok=True)
            for d in os.listdir(os.path.join(ff, "Config")):
                for cf in os.listdir(os.path.join(ff, "Config", d)):
                    ffp = os.path.join(ff, "Config", d, cf)
                    print("Copying %r to %r"%(cf, tdir))
                    shutil.copy2(ffp, os.path.join(tdir, cf))