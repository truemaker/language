from tokens import *

class Preprocessor:
    def preprocess(self, tokens):
        preprocessed_tokens = []
        for token in tokens:
            if token.type == TT_PREPROCESS:
                if token.value == 'equals':
                    pos_start = token.pos_start
                    tok_type = TT_EE
                    preprocessed_tokens.append(Token(tok_type, pos_start, token.pos_end))
                elif token.value == 'import':
                    pos_start = token.pos_start
                    tok_type = TT_IDENTIFIER
                    preprocessed_tokens.append(Token(tok_type, pos_start=pos_start, pos_end=token.pos_end, value='run'))
            else:
                preprocessed_tokens.append(token)
        return preprocessed_tokens
