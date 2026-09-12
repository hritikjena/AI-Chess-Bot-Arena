import os
import sys

try:
    from google import genai
except ImportError:
    genai = None

def get_commentary(board_fen, move_san, prev_analysis, new_analysis):
    """
    Generates AI commentary for a significant shift in evaluation.
    prev_analysis and new_analysis contain score, best_move, and pv.
    """
    if prev_analysis is None or new_analysis is None:
        return None
        
    prev_score = prev_analysis.get("score")
    new_score = new_analysis.get("score")
    
    if prev_score is None or new_score is None:
        return None
        
    swing = abs(new_score - prev_score)
    
    # Only comment on significant swings (e.g., > 1.5 pawns)
    if swing < 150:
        return None
        
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return "[Error] Gemini API key is not configured."
        
    if genai is None:
        return "[Error] Google GenAI SDK is not available."
            
    try:
        client = genai.Client(api_key=api_key)
        
        eval_before = prev_score / 100.0
        eval_after = new_score / 100.0
        eval_loss = abs(eval_after - eval_before)
        best_move = prev_analysis.get("best_move", "Unknown")
        pv = prev_analysis.get("pv", "Unknown")
        
        prompt = f"""
        You are a highly analytical but energetic chess grandmaster commentating an AI bot tournament.
        Explain the provided engine evaluation in one or two punchy sentences.

        ENGINE DATA (DO NOT MODIFY OR INVENT THIS DATA):
        - FEN before: {board_fen}
        - Played move: {move_san}
        - Stockfish Best Move was: {best_move}
        - Evaluation before: {eval_before:+.2f}
        - Evaluation after: {eval_after:+.2f}
        - Evaluation loss: {eval_loss:.2f} pawns
        - Principal Variation: {pv}

        RULES:
        1. Stockfish is authoritative for numerical evaluation.
        2. Do not invent engine variations or a best move.
        3. Explain WHY the supplied move was a mistake or brilliant based on the evaluation shift.
        4. Use concise chess terminology.
        5. If the supplied engine data is insufficient to explain something, simply mention the evaluation shift.
        6. Do not include the raw data block in your output, just write the conversational explanation.
        """
        
        model_name = os.getenv("GEMINI_MODEL", "gemini-3.6-flash")
        
        response = client.models.generate_content(
            model=model_name,
            contents=prompt,
        )
        return response.text.strip()
    except Exception as e:
        err_msg = str(e).lower()
        if "not found" in err_msg and "model" in err_msg:
            return f"[Error] Configured Gemini model ({model_name}) is unavailable. Check GEMINI_MODEL."
        elif "quota" in err_msg or "rate limit" in err_msg:
            return "[Error] API quota or rate limit exceeded. Please try again later."
        else:
            print(f"Gemini API Error: {str(e)}") # Log to backend stdout
            return "[Error] The AI commentary service encountered an internal error."
