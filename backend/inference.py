def run_inference(model, data, paradigm):
    if paradigm == "ml":
        return model.predict(data).tolist()
    elif paradigm == "dl":
        model.eval()
        with torch.no_grad():
            return model(data).tolist()
    return None
