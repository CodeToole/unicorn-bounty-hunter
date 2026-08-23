import os
import shutil

def harvest():
    os.makedirs("static/assets", exist_ok=True)
    os.makedirs("static/videos", exist_ok=True)
    os.makedirs("static/css", exist_ok=True)

    # Copy images
    if os.path.exists("web/images"):
        for item in os.listdir("web/images"):
            src = os.path.join("web/images", item)
            dst = os.path.join("static/assets", item)
            if os.path.isfile(src):
                shutil.copy2(src, dst)
                print(f"Copied image: {item} -> static/assets/{item}")

    # Copy videos
    if os.path.exists("web/videos"):
        for item in os.listdir("web/videos"):
            src = os.path.join("web/videos", item)
            dst = os.path.join("static/videos", item)
            if os.path.isfile(src):
                shutil.copy2(src, dst)
                print(f"Copied video: {item} -> static/videos/{item}")

    # Copy favicons
    for f in ["favicon.ico", "favicon.jpg"]:
        src = os.path.join("web", f)
        if os.path.exists(src):
            shutil.copy2(src, os.path.join("static/assets", f))
            shutil.copy2(src, os.path.join("static", f))
            print(f"Copied favicon: {f}")

    print("Harvest complete!")

if __name__ == "__main__":
    harvest()
