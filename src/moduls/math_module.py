import language.models.message_constant as mc
from answer import AssistantAnswer

class MathModule:
    def run(self, assistant, parameters_dict):
        intent = parameters_dict["Intent"]
        if intent == "Welcome":
            answer = AssistantAnswer(mc.MATH_MODULE_INTRODUCTION_MESSAGE)
        elif intent == "Solving mathematical tasks":
            request = parameters_dict["Request"]
            answer = AssistantAnswer(None, message_str="User asked: {}".format(request))
        return answer
