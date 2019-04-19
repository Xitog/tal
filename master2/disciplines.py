
# --chargement du dictionnaire de recodage ---
recode=dict()
entree=open("recodage-josette.tsv", mode="r", encoding="UTF8")
header=entree.readline()
for line in entree:
     line=line.rstrip("\n")
     t=line.split("\t")
     recode[t[0]]=t[3]
entree.close()


def domain(domains):
     champs = domains.split(",")
     dom=""
     for c in champs:
          if (c.startswith("0") or c.startswith("1")) and c != "0.shs":
               if c in recode:
                    return recode[c] #premier domaine recodé uniquement
               else:
                    return 'RECODE FAIL'

if __name__ == '__main__':
     # --- construction du dictionnaire id -> champ recodé  ---
     domaines=dict()
     entree=open("total-articles-HAL.tsv", mode="r", encoding="UTF8")
     for line in entree:
          line=line.rstrip("\n")
          t=line.split("\t")
          id=t[0]
          champs = t[3].lstrip('"').rstrip('"').split(",")
          dom=""
          for c in champs:
              if (c.startswith("0") or c.startswith("1")) and c != "0.shs":
                  dom=recode[c]
                  break #premier domaine recodé uniquement
          domaines[id]=dom
     entree.close()
