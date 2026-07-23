class HookRegistry:

    before = {}
    after = {}

    #here we will to save all the functions that the plugins create 
    #this function is run before that the function major of the business logic
    @classmethod
    def register_before(cls, action, callback):

        if action not in cls.before:
            cls.before[action] = []

        cls.before[action].append(callback)


    #here we will to save all the functions that the plugins create 
    #this function is run after that the function major of the business logic
    @classmethod
    def register_after(cls, action, callback):

        if action not in cls.after:
            cls.after[action] = []

        cls.after[action].append(callback)