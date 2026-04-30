import sys
from tdl.queue.queue_based_implementation_runner import QueueBasedImplementationRunnerBuilder
from tdl.runner.challenge_session import ChallengeSession

from entry_point_mapping import EntryPointMapping
from runner.utils import Utils
from runner.user_input_action import get_user_input


"""
  ~~~~~~~~~~ Running the system: ~~~~~~~~~~~~~
 
    From IDE:
       Run this file from the IDE.
 
    From command line:
       PYTHONPATH=lib python lib/send_command_to_server.py
 
    To run your unit tests locally:
       PYTHONPATH=lib python -m pytest -q test/solution_tests/
 
  ~~~~~~~~~~ The workflow ~~~~~~~~~~~~~
 
    By running this file you interact with a challenge server.
    The interaction follows a request-response pattern:
         * You are presented with your current progress and a list of actions.
         * You trigger one of the actions by typing it on the console.
         * After the action feedback is presented, the execution will stop.
 
    +------+-----------------------------------------------------------------------+
    | Step | The usual workflow                                                    |
    +------+-----------------------------------------------------------------------+
    |  1.  | Run this file.                                                        |
    |  2.  | Start a challenge by typing "start".                                  |
    |  3.  | Read the description from the "challenges" folder.                    |
    |  4.  | Locate the file corresponding to your current challenge in:           |
    |      |   ./lib/solutions                                                     |
    |  5.  | Replace the following placeholder exception with your solution:       |
    |      |   raise NotImplementedError()                                         |
    |  6.  | Deploy to production by typing "deploy".                              |
    |  7.  | Observe the output, check for failed requests.                        |
    |  8.  | If passed, go to step 1.                                              |
    +------+-----------------------------------------------------------------------+
 
    You are encouraged to change this project as you please:
         * You can use your preferred libraries.
         * You can use your own test framework.
         * You can change the file structure.
         * Anything really, provided that this file stays runnable.
 
"""

entry_point_mapping = EntryPointMapping()

runner = QueueBasedImplementationRunnerBuilder()\
    .set_config(Utils.get_runner_config())\
    .with_solution_for('amazing_maze', entry_point_mapping.amazing_maze) \
    .with_solution_for('array_sum', entry_point_mapping.array_sum)\
    .with_solution_for('checkout', entry_point_mapping.checkout)\
    .with_solution_for('count_lines', entry_point_mapping.count_lines)\
    .with_solution_for('filter_pass', entry_point_mapping.filter_pass)\
    .with_solution_for('fizz_buzz', entry_point_mapping.fizz_buzz)\
    .with_solution_for('hello', entry_point_mapping.hello)\
    .with_solution_for('increment', entry_point_mapping.increment)\
    .with_solution_for('int_range', entry_point_mapping.int_range)\
    .with_solution_for('inventory_add', entry_point_mapping.inventory_add)\
    .with_solution_for('inventory_get', entry_point_mapping.inventory_get)\
    .with_solution_for('inventory_size', entry_point_mapping.inventory_size)\
    .with_solution_for('letter_to_santa', entry_point_mapping.letter_to_santa)\
    .with_solution_for('rabbit_hole', entry_point_mapping.rabbit_hole) \
    .with_solution_for('render_house', entry_point_mapping.render_house) \
    .with_solution_for('sum', entry_point_mapping.sum)\
    .with_solution_for('to_uppercase', entry_point_mapping.to_uppercase)\
    .with_solution_for('ultimate_maze', entry_point_mapping.ultimate_maze) \
    .with_solution_for('waves', entry_point_mapping.waves)\
    .with_solution_for('enqueue', entry_point_mapping.enqueue) \
    .with_solution_for('dequeue', entry_point_mapping.dequeue) \
    .with_solution_for('size', entry_point_mapping.size) \
    .with_solution_for('purge', entry_point_mapping.purge) \
    .with_solution_for('age', entry_point_mapping.age) \
    .create()

ChallengeSession\
    .for_runner(runner)\
    .with_config(Utils.get_config())\
    .with_action_provider(lambda: get_user_input(sys.argv[1:]))\
    .start()
