from sparv.api import Annotation, Output, annotator, get_logger, Config
from transformers import AutoTokenizer, AutoModelForTokenClassification
import torch    
import os

logger = get_logger(__name__)

@annotator("Annotate the data with PI entities.", 
           language=["swe"],
           config = [
               Config("sbx_pi_detection.annotation_level", default="detailed_iob", description="Annotation type (and, consequently, model) to use.")
           ]
           )
def pi_detection(
    word: Annotation = Annotation("<token:word>"),
    out: Output = Output("<token>:sbx_pi_detection.pi"),
    annotation_level: str = Config("sbx_pi_detection.annotation_level")
    ):
    # get the model path when the model comes with the plugin
    # set up tokenizer and model
    try:
        tokenizer = AutoTokenizer.from_pretrained(MODELS[annotation_level])
        model = AutoModelForTokenClassification.from_pretrained(MODELS[annotation_level])
    except:
        logger.warning(f"The requested annotation type {annotation_level} does not exist. Defaulting to detailed_iob.")
        tokenizer = AutoTokenizer.from_pretrained(MODELS['detailed_iob'])
        model = AutoModelForTokenClassification.from_pretrained(MODELS['detailed_iob'])

    # chunk the input to max model length
    subsplits = trim_to_max_len([val for val in word.read()], tokenizer)  
    # get model predictions for subword tokens
    predictions = [get_preds(subsplit, tokenizer, model) for subsplit in subsplits]
    # flatten
    predictions = [pred for subsplit in predictions for pred in subsplit]
    # write predictions out
    out.write([p[1] for p in predictions])

def trim_to_max_len(
    text: list,
    tokenizer: AutoTokenizer,
    max_len: int = 512,
    ):
    max_len -= tokenizer.num_special_tokens_to_add()
    subsplits = []
    current_subsplit = []
    current_len = 0
    
    # sum lengths of tokenized tokens until the maximum, split
    for element in text:
        tokenized = tokenizer.tokenize(element)
        current_sublen = len(tokenized)
        if current_sublen == 0:
            continue
        elif (current_len + current_sublen) > max_len:
            subsplits.append(current_subsplit)
            current_subsplit = [element]
            current_len = current_sublen   
        else:  # it's within the length
            current_subsplit.append(element)
            current_len += current_sublen
    subsplits.append(current_subsplit)
       
    return subsplits

def get_preds(
    text: list,
    tokenizer: AutoTokenizer,
    model: AutoModelForTokenClassification,
):
    # get model predictions
    inputs = tokenizer(text, is_split_into_words=True, return_tensors="pt")
    with torch.no_grad():
        logits = model(**inputs).logits
    predictions = torch.argmax(logits, dim=2)
    predicted_token_class = [model.config.id2label[t.item()] for t in predictions[0]]
    
    # realign predictions to words
    words_and_preds = []
    current_word_idx = 0
    current_preds = []
    for i, orig_word_idx in enumerate(inputs.word_ids()):
        if orig_word_idx == None:
            continue
        elif orig_word_idx == current_word_idx:
            current_preds.append(predicted_token_class[i])
        else:  # next word
            # close off the previous word
            words_and_preds.append((current_word_idx, current_preds))
            # next word
            current_word_idx = orig_word_idx
            current_preds = [predicted_token_class[i]]
    words_and_preds.append((current_word_idx, current_preds))
    
    # subword token predictions -> token predictions heuristic
    one_pred_per_word = []
    for item in zip(text, words_and_preds):
        word_predictions = list(set(item[1][1]))
        if len(word_predictions) > 1:
            if 'O' in word_predictions:
                word_predictions.remove('O')  # replace with another if needed
            word_predictions = [word_predictions[0]]  # the final prediction is the first one from the set left after removing O if multiple predictions per word are present, assuming that the first element is more "core" to the word's meaning
        one_pred_per_word.append((item[0], word_predictions[0]))
         
    return one_pred_per_word

MODELS = {
    'basic': 'sbx/KB-bert-base-swedish-cased_PI-detection-basic',
    'basic_iob': 'sbx/KB-bert-base-swedish-cased_PI-detection-basic-iob',
    'detailed': 'sbx/KB-bert-base-swedish-cased_PI-detection-detailed',
    'detailed_iob': 'sbx/KB-bert-base-swedish-cased_PI-detection-detailed-iob',
    'general': 'sbx/KB-bert-base-swedish-cased_PI-detection-general',
    'general_iob': 'sbx/KB-bert-base-swedish-cased_PI-detection-general-iob'
}