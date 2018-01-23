import language.models.message_constant as mc
from answer import AssistantAnswer


class SelfIntroductionModule:
    HEAD_PATTERN = "{} - {}"
    INTENT_PATTERN = "   {}"

    def run(self, assistant, parameters_dict):
        apps = assistant.application_dict
        lines = []
        for app_name, app_desc in apps.items():
            lines.append(SelfIntroductionModule.HEAD_PATTERN.format(app_desc.get_name(), app_desc.get_description()))
            for intent in app_desc.get_intents_list():
                line = SelfIntroductionModule.INTENT_PATTERN.format(intent.get_name())
                lines.append(line)
        lines = "\n".join(lines)
        answer = AssistantAnswer(mc.INTRODUCTION_MESSAGE, parameters_dict={"desc": lines})
        return answer
