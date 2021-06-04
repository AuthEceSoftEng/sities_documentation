## RASA Configuration

ELSA uses a local [RASA](https://rasa.com/) model to handle conversation. This gives a more robust conversational system leading to better user experience.
RASA's development is story-driven. This means you have to define conversations using intents and responses.
Of course you can have your own conversation handler but first you have to call it from our RASA system as shown in the [last section](#initialize-a-custom-application).

Our system uses RASA v1 at the moment and you can find further documentation about it [here](https://legacy-docs-v1.rasa.com/). It records the user's expressions and plays the assistant's answers in a constant process. However, all device's functionalities, such as custom sounds, recordings or screen usage can only be used by creating your own complete application which will be called from RASA's action server as shown [here](#initialize-a-custom-application).


### RASA Files
In order to integrate your application to the generic RASA system 4 different files are needed:

* [domain.yml](#domain.yml)
* [nlu.md](#nlu.md)
* [stories.md](#stories.md)
* [actions.py](#actions.py)

Their basic contexts are presented first and then some more advanced issues are discussed. Most of the examples shown below are also presented in the
4 separate files you can find in this directory. They are not 100% prefect or fully functional, they are here to give you an image on how to integrate your application with RASA.

#### nlu.md

For an assistant to recognize what a user is saying no matter how the user phrases their message, we need to provide example messages the assistant can learn from. We group these examples according to the idea or the goal the message is expressing, which is also called the intent. In the code block below we have added an intent called greet, which contains example messages like "Γειά", “Γειά σου” and “Καλημέρα”.

Intents and their examples are used as training data for the assistant's Natural Language Understanding (NLU) model.

```
## intent:greet
- Γειά
- Γειά σου
- Καλημέρα
- Καλησπέρα
```

**Tip**: Try to create several examples for every intent (around 10 is a good start) so that the model will have better chances of understanding the intents correctly.

You can also use regular expressions and lookup tables as explained [here](https://legacy-docs-v1.rasa.com/nlu/training-data-format/) but we advise you to keep them all in the `nlu.md` file. All other files will be ignored by our system.

#### stories.md

Stories are example conversations that train an assistant to respond correctly depending on what the user has said previously in the conversation. The story format shows the intent of the user message followed by the assistant’s action or response.

Your first story should show a conversation flow where the assistant helps the user accomplish their goal in a straightforward way (happy paths). Later, you can add stories for situations where the user doesn't want to provide their information or switches to another topic (unhappy paths).

**Tip**: Write several stories, in order to handle any possible case. Happy paths are not as common as you may think.

In the code block below, we have added a story where the user and assistant exchange greetings, the assistant asks the user about his mood, he answers happily and the assistant answers she is glad.

The name your story comes after `##`. This is only for debugging reasons so you can set it whatever you like but we suggest you set it something that will help you during development. User's intents start with `*` and your model's responses start with `-`. The utterances will be defined in detail in the `domain.yml` file.

```
## greet happy path
* greet
  - utter_greet
* mood_great
  - utter_happy
```


#### domain.yml

This file is the most important one. It defines explicitly all your model's configurations, the world in which the assistant will operate.
In this file you list all your intents, responses, entities, slots, forms and actions you want the assistant to understand and handle.

###### Intents

We talked above about intents. Here you have to list which intents you want the assistant to learn during training. In the next example we use 4 intents:

```
intents:
  - greet
  - mood_great
  - bye
  - thank
```

###### Responses

Responses are expressions the assistant will say as an answer to an intent. Every response has to start with `utter_` and it can have multiple expressions. The assistant will use one of them each time.

```
responses:
  utter_greet:
  - text: Γειά σου! Τι κάνεις;
  - text: Γειά! Πώς μπορώ να βοηθήσω;
  utter_happy:
  - text: Τέλεια, συνέχισε έτσι!
```

###### Slots

Slots hold information you want to keep track of during a conversation. They are the assistant's memory. They act as a key-value store which can be used to store information the user provided (e.g their home city or name) as well as information gathered about the outside world (e.g. the result of a database query).

Most of the time, you want slots to influence how the dialogue progresses. There are different slot types for different behaviors and you can learn more about them [here](https://legacy-docs-v1.rasa.com/core/slots/).

In the next example we specify one slot, which we want to store the user's name.

```
slots:
  user_name:
    type: text
```

You can also use slot values inside the assistant's response messages, like that:

```
responses:
  utter_greet:
  - text: Γειά σου {user_name}! Τι κάνεις;

```

###### Entities

Entities are structured pieces of information inside a user message. The entities section lists all entities extracted by the assistant during the conversation.

If, let's say, we want the user to tell us his name we create the entity `user_name` and the assistant will locate it during the conversation (we will explain later how). We set the entity's name exactly the same with a slot's name, so that when the entity will be extracted, it will be stored it the slot and it will be accessible throughout the rest of the conversation. There is also a custom entity-slot mapping explained in the actions section.

```
entities:
  - user_name
```

For entity extraction to work, you need to give the assistant many examples to learn from. This means, you have to create example sentences for intents that contain these entities you want to recognize. In the previous case, where we want to extract the user's name, we should create the following intent.

```
## intent:user_name
- Είμαι ο [γιώργος](user_name)
- Είμαι ο [νίκος](user_name)
- Με λένε [κώστα](user_name)
- Είμαι η [μαρία](user_name)
- [γιάννης](user_name)
- [δήμητρα](user_name)
```

You get the idea.

**Note** that you should use only lowercase letters because the used speech to text algorithms are case insensitive and your data should also contain such examples.

You can see more examples [here](https://legacy-docs-v1.rasa.com/nlu/training-data-format/) and [here](https://legacy-docs-v1.rasa.com/nlu/entity-extraction/).


###### Actions

When you want the assistant to respond with custom messages or with data retrieved from an API or a database, you need a custom action instead of an ordinary response. Actions are listed in the `domain.yml` file as below. They are pure Python scripts written in the `actions.py` file that do much more than to utter a message.

```
actions:
- action_get_user_name
- action_greet
```

**Note**: RASA uses internally several actions to make every conversation work. They are listed [here](https://legacy-docs-v1.rasa.com/core/actions/#default-actions) and should not be overridden. If you use one of these names for an action, our system will change it and we can't guarantee your application's correct functionality.

###### Forms

One of the most common conversation patterns is to collect a few pieces of information from a user in order to do something (book a restaurant, call an API, search a database, etc.). This is also called **slot filling**. Forms are an easy way to collect data from the user and fill them to the corresponding slots. If you need to collect multiple pieces of information in a row, we recommended that you create a form to handle them. Otherwise, if you want to extract just one entity, like the user_name as above, we advise you not to use forms. They will complicate the model without any true benefit.

Forms are defined in the `domain.yml` file like this.

```
forms:
  - name_form
```

There has to be a story that contains them. In this story the user intent is setup_name, which is followed by the form action name_form. With form{"name": "name_form"} the form is activated and with form{"name": null} the form is deactivated again, after all slots are filled. The bot can execute any kind of actions outside the form while the form is still active. On the “happy path”, where the user is cooperating well and the system understands the user input correctly, the form is filling all requested slots without interruption. You can see more details about handling unhappy paths of forms [here](https://legacy-docs-v1.rasa.com/core/forms/). Actually all happy paths are represented with just this one story.

```
## form happy path
* setup_name
  - name_form
  - form{"name": "name_form"}
  - form{"name":null}
```

Forms can use a custom action for further handling customizations. `FormAction` is presented in the [next section](#formaction).


### actions.py

Custom actions are used as response to user's intents. Their format is explained next.

First, the Action class is imported and inherited in our custom action.

```
from rasa_sdk.actions import Action

class ActionGreet(Action):

```

This class has 2 mandatory methods:
* `name`: Defines the action's name. The name returned by this method is the one used in your bot's domain.
* `run`: Executes the side effects of the action.

  **Parameters**:
    * `dispatcher` – the dispatcher which is used to send messages back to the user. Use:
      * `dispatcher.utter_message()` or
      *  any other `rasa_sdk.executor.CollectingDispatcher` method
    * `tracker` – the state tracker for the current user. You can access:
      * slot values using `tracker.get_slot(slot_name)`
      * the most recent user message is `tracker.latest_message.text`,
      * any other `rasa_sdk.Tracker` property from [here](https://legacy-docs-v1.rasa.com/api/tracker/)
    * `domain` – the bot's domain

```
  def name(self):
      return 'action_greet'

  def run(self, dispatcher, tracker, domain):
      dispatcher.utter_message(template="utter_greet")
      return []
```

###### FormAction

This is a single action which contains the logic to loop over the required slots and ask the user for information. The `FormAction` will only request slots which haven’t already been set.

You need to define 3 methods:

* `name`: the unique identifier name of the form, as defined in the `domain.yml`.
* `required_slots`: a list of all required slots the form needs to fill.
* `submit`: contains what the form has to do after all required slots are filled. It is like the `run` method. If there is not submit method, the assistant will continue normally with the current story.

In addition, every time a slot is not filled the form action will try to ask for an entity automatically using a response called `utter_ask_{slot_name}`, so you will have to add these in the `domain` file.

```
from rasa_sdk.forms import FormAction

class NameForm(FormAction):
  def name(self):
    return 'name_form'

  @staticmethod
  def required_slots(tracker: Tracker):
    return ["user_name"]

  def submit(self, dispatcher, tracker, domain):
      dispatcher.utter_message(template = "utter_submit")
      return []
```

If you do not define slot mappings, slots will be only filled by entities with the same name as the slot that are picked up from the user input.
`FormAction` can also support yes/no questions and free-text input. These customizations are defined with the next method.


* `slot_mappings`

This example is taken from the official RASA docs. It is about a restaurant bot that maps its different slots with multiple ways. You can find more details about it [here](https://legacy-docs-v1.rasa.com/core/forms/).

```
def slot_mappings(self):
    """
        A dictionary to map required slots to
          - an extracted entity
          - intent: value pairs
          - a whole message
        or a list of them, where a first match will be picked
    """

    return {
        "cuisine": self.from_entity(entity="cuisine", not_intent="chitchat"),
        "num_people": [
            self.from_entity(
                entity="number", intent=["inform", "request_restaurant"]
            ),
        ],
        "outdoor_seating": [
            self.from_entity(entity="seating"),
            self.from_intent(intent="affirm", value=True),
            self.from_intent(intent="deny", value=False),
        ],
        "preferences": [
            self.from_intent(intent="deny", value="no additional preferences"),
            self.from_text(not_intent="affirm"),
        ],
        "feedback": [self.from_entity(entity="feedback"), self.from_text()],
    }
```

#### Events

Conversations in Rasa are represented as a sequence of [events](https://legacy-docs-v1.rasa.com/api/events/). This means actions that you want to create, can be accomplished using RASA's events.
We list some common ones below.

###### Set/Delete Slot

You can set or delete a value of a slot inside a custom action. You have to inlude this `from rasa_sdk.events import SlotSet` and
you can set a slot to a specific value you can use `SlotSet(key=key, value=value)` where `key` is your slot's name and `value` its new value.
If you want to empty this slot, just set `value = None`.

**Note**: Never reset all slots! This might create an error to the rest of ELSA's applications and features.

###### Schedule Reminders

You can schedule an event to be triggered in the future. You can use this class
`class rasa.core.events.ReminderScheduled(intent, trigger_date_time, entities=None, name=None, kill_on_user_message=True, timestamp=None, metadata=None)` to schedule the asynchronous triggering of a user intent (with entities if needed) at a given time.

You can also cancel an already set event with this class `class rasa.core.events.ReminderCancelled(name=None, intent=None, entities=None, timestamp=None, metadata=None)`.

### Initialize A Custom Application
