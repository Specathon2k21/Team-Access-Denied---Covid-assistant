import spacy

nlp = spacy.load('en_core_web_sm')
doc = nlp("i need a vitamin c tablet at 9 am")

entities = []
for ent in doc.ents:
    entities.append(ent)
print(entities)