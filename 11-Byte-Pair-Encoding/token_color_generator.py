import gradio as gr
import json

# Load token-to-color mappings from a JSON file
def load_token_colors(filename):
    with open(filename, "r") as file:
        return json.load(file)

token_colors = load_token_colors("token_colors.json")

# Counts the occurrences of consecutive pairs of elements in the ids list and returns a dictionary with these pairs as keys and their counts as values.
def get_stats(ids):
    counts = {}
    for pair in zip(ids, ids[1:]):
        counts[pair] = counts.get(pair, 0) + 1
    return counts


def load_merges(filename):
    """Load the merges dictionary from a JSON file."""
    with open(filename, "r") as file:
        loaded_data = json.load(file)
        return {eval(key): value for key, value in loaded_data.items()}


def merge(ids, pair, idx):
    """Merge consecutive pairs of elements in the list."""
    newids = []
    i = 0
    while i < len(ids):
        if i < len(ids) - 1 and ids[i] == pair[0] and ids[i + 1] == pair[1]:
            newids.append(idx)
            i += 2
        else:
            newids.append(ids[i])
            i += 1
    return newids


def encode(text, merges):
    """Encode a string into tokens using a merge table."""
    tokens = list(text.encode("utf-8"))
    
    while len(tokens) >= 2:
        stats = get_stats(tokens)
        pair = min(stats, key=lambda p: merges.get(p, float("inf")))
        
        if pair not in merges:
            break
        
        idx = merges[pair]
        tokens = merge(tokens, pair, idx)
    
    return tokens


def decode(ids, vocab):
    """Decode a list of token IDs back into a string."""
    tokens = b"".join(vocab[idx] for idx in ids)
    text = tokens.decode("utf-8", errors="replace")
    return text


merges = load_merges("hindi_bpe.json")

vocab = {idx: bytes([idx]) for idx in range(256)}
for (p0, p1), idx in merges.items():
    vocab[idx] = vocab[p0] + vocab[p1]


def encode_and_highlight(text):
    """Encode text and highlight tokens based on ID."""
    tokens = encode(text, merges)
    highlighted_text = ""
    
    for token in tokens:
        color = token_colors.get(str(token), "#E0E0E0")
        highlighted_text += f'<span style="background-color: {color}; padding: 2px; border-radius: 5px; margin: 2px">{token}</span> '
    
    return highlighted_text


def decode_tokens_with_highlight(token_string):
    """Decode a comma-separated string of token IDs and highlight the output."""
    try:
        token_ids = list(map(int, token_string.split(',')))
        decoded_text = decode(token_ids, vocab)
        highlighted_text = ""
        
        for token_id in token_ids:
            color = token_colors.get(str(token_id), "#E0E0E0")
            highlighted_text += f'<span style="background-color: {color}; padding: 2px; border-radius: 5px; margin: 2px">{chr(token_id)}</span>'
        
        return highlighted_text if highlighted_text else decoded_text
    except Exception as e:
        return f"Error decoding tokens: {e}"


def app_interface():
    with gr.Blocks() as demo:
        gr.Markdown("## Byte Pair Encoder & Decoder App")
        gr.Markdown("Enter text and see encoded tokenized output, or decode a list of tokens back to highlighted text!")
        
        with gr.Tab("Encode & Highlight"):
            text_input = gr.Textbox(label="Input Text")
            output_box = gr.HTML(label="Tokenized Output")
            submit_button = gr.Button("Highlight Tokens")
            submit_button.click(
                fn=encode_and_highlight,
                inputs=text_input,
                outputs=output_box
            )
        
        with gr.Tab("Decode Tokens"):
            token_input = gr.Textbox(label="Input Token IDs (comma-separated)")
            decoded_output = gr.HTML(label="Highlighted Decoded Text")
            decode_button = gr.Button("Decode Tokens")
            decode_button.click(
                fn=decode_tokens_with_highlight,
                inputs=token_input,
                outputs=decoded_output
            )
        
    return demo


# Launch the app
app = app_interface()
app.launch()

