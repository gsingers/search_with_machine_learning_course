from sentence_transformers import SentenceTransformer
model = SentenceTransformer('paraphrase-MiniLM-L6-v2')
sentences = ['This framework generates embeddings for each input sentence', 'Including this one']
embeddings = model.encode(sentences)


