import os, re, sys
ROOT = sys.argv[1] if len(sys.argv) > 1 else "."
pat = re.compile(r"\b(3\.0|3\.5|5\.0|6\.0|10\.0|12\.0|1\.2|2\.0|0\.90|0\.92|0\.94|0\.97|0\.98)\b")
hits=[]
for dp,_,fns in os.walk(ROOT):
    for fn in fns:
        if fn.endswith(".py"):
            p=os.path.join(dp,fn)
            try:
                txt=open(p,"r",encoding="utf-8").read()
            except:
                continue
            if pat.search(txt):
                hits.append(os.path.relpath(p, ROOT))
print("HITS", len(hits))
for h in hits[:200]:
    print(h)
