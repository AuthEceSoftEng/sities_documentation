from rasa_sdk.actions import Action
from rasa_sdk.forms import FormAction

class ActionGreet(Action):

    def name(self):
      return 'action_greet'

  def run(self, dispatcher, tracker, domain):
      dispatcher.utter_message(template="utter_greet")
      return []


class NameForm(FormAction):

    def name(self):
      return 'name_form'

    @staticmethod
    def required_slots(tracker):
      return ["user_name"]

    def submit(self, dispatcher, tracker, domain):
        dispatcher.utter_message(template = "utter_submit")
        return []
