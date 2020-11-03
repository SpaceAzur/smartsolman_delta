import asyncio, time, asyncio
from collections import deque

STATUS_NEW = 'NEW'
STATUS_RUNNING = 'RUNNING'
STATUS_FINISHED = 'FINISHED'
STATUS_ERROR = 'ERROR'

class Task:
    def __init__(self, coro):
        self.coro = coro
        self.name = coro.__name__
        self.status = STATUS_NEW
        self.return_value = None
        self.error_value = None

    # execute la tache jusqu'a la prochaine pause
    def run(self):
        try:
        # on passe la tache a l'état RUNNING et on l'execute jusqu'a
        # la prochaine suspension de la routine
            self.status = STATUS_RUNNING
            next(self.coro)
        except StopIteration as err:
            # si al coroutine se termine, la tache passe a l'etat FINISHED
            # et on recupere sa valeur de retour
            self.status = STATUS_FINISHED
            self.return_value = err.value
        except Exception as err:
            # si une autre exception est levé durant l'execution de la 
            # coroutine, la tache passe a l'etat ERROR, et on recupere
            # l'exception pour laisser l'utilisateur la traiter
            self.status = STATUS_ERROR
            self.error_value = err
    
    def is_done(self):
        return self.status in {STATUS_FINISHED, STATUS_ERROR}
    
    def __repr__(self):
        result = ''
        if self.is_done():
            result = " ({!r})".format(self.return_value or self.error_value)
        
        return "<Task '{}' [{}]{}>".format(self.name, self.status, result)


class Loop:
    def __init__(self):
        self._running = deque()
    
    def _loop(self):
        task = self._running.popleft()
        task.run()
        if task.is_done():
            print(task)
            return
        self.schedule(task)
    
    def run_until_empty(self):
        while self._running:
            self._loop()
    
    def schedule(self, task):
        if not isinstance(task, Task):
            task = Task(task)
        self._running.append(task)
        return task

    # methode pour executer une coroutine en particulier en entier
    def run_until_complete(self, task):
        task = self.schedule(task)
        while not task.is_done():
            self._loop()

def tic_tac():
    print("Tic")
    yield
    print("Tac")
    yield
    return "Boum!"

task = Task(tic_tac())

# une instance de la class Task qui informe sur l'état de la coroutine
while not task.is_done():
    task.run()
    print(task)

print("\n========\n")

# un exemple d'execution concurrente de la coroutine
# instanciation d'une file d'attente
running_tasks = deque()
# 2 tâches s'ajoute à la file d'attente
running_tasks.append(Task(tic_tac()))
running_tasks.append(Task(tic_tac()))

# tant que des tâches sont en attentes
while running_tasks:
    # je récupère la plus ancienne tâche
    task = running_tasks.popleft()
    # je la traite
    task.run()
    # si la tache est terminé
    if task.is_done():
        # je l'affiche
        print(task)
    # sinon
    else:
        # on la replace au bout de la file d'attente
        running_tasks.append(task)


def spam():
    print("SPam")
    yield
    print("Eggs")
    yield
    print("Bacon")
    yield
    return "SPAM!!!"

print("\n=======\n")

event_loop = Loop()
event_loop.schedule(tic_tac())
event_loop.schedule(spam())
event_loop.run_until_empty()

print("\n=======\n")

event_loop = Loop()
event_loop.run_until_complete(tic_tac())

print("\n======= asyncio\n")

loop = asyncio.get_event_loop()
loop.run_until_complete(tic_tac())
print()
loop.run_until_complete(asyncio.wait([tic_tac(), spam()]))
