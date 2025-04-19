import torch
import clip
import sys
from io import BytesIO
from PIL import Image

def get_dict_size(dictionary):
    total_size = sys.getsizeof(dictionary)  # Get the size of the dictionary object itself
    for key, value in dictionary.items():
        total_size += sys.getsizeof(key)  # Add the size of the key
        total_size += sys.getsizeof(value)  # Add the size of the value
        print("key size:", sys.getsizeof(key))
        print("value size:", sys.getsizeof(value))
    return total_size

class SimilarityCalculator:
    def __init__(self):
        self.device = self._get_device()
        self.model, self.preprocess = self._initialize_model("ViT-B/32", self.device)
        self.cosine_similarity = torch.nn.CosineSimilarity(dim=0)
        self.image_1 = None
        self.image_2 = None
        self.image_cache = {}
        self.raw_similarity = None

    def _get_device(self):
        return "cuda" if torch.cuda.is_available() else "cpu"

    def _initialize_model(self, model_name="ViT-B/32", device="cpu"):
        model, preprocess = clip.load(model_name, device=device)
        return model, preprocess

    def _embed_image(self, image_path):
        preprocessed_image = (
            self.preprocess(Image.open(BytesIO(image_path))).unsqueeze(0).to(self.device)
        )
        image_embeddings = self.model.encode_image(preprocessed_image)
        # print(len(image_embeddings),image_embeddings.shape)
        # print("Shape:", image_embeddings.shape)
        # print("Dtype:", image_embeddings.dtype)
        # print("Device:", image_embeddings.device)
        # print("Is contiguous:", image_embeddings.is_contiguous())
        # print("Requires grad:", image_embeddings.requires_grad)
        # print("Total bytes (raw):", image_embeddings.element_size() * image_embeddings.nelement(), "bytes")
        return image_embeddings

    def calculate_similarity(self, image_path_1, image_path_2):
        if image_path_1 not in self.image_cache:
            self.image_cache[image_path_1] = self._embed_image(image_path_1)

        if image_path_2 not in self.image_cache:
            self.image_cache[image_path_2] = self._embed_image(image_path_2)

        # Retrieve the embeddings from the cache
        image_1 = self.image_cache[image_path_1]
        image_2 = self.image_cache[image_path_2]
        self.image_cache.clear()
        self.raw_similarity = self.cosine_similarity(
            image_1[0], image_2[0]
        ).item()
        return self.raw_similarity
