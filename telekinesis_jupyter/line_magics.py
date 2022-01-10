import asyncio
from collections import deque

from IPython.core.magic import register_line_cell_magic

class RemoteKernels:
    def __init__(self, *instances, print_callback=print, input_callback=input):
        self.instances = deque(instances)
        self.last_magic = None
        self.magic_history = []
        
        async def register_line_magics():
            await asyncio.sleep(0.00000001)
            self_name = [ k for k,v in globals().items() if v is self][0]
            
            @register_line_cell_magic(f'{self_name}.call_one')
            def call_one(line, cell):
                args, kwargs = [], {}
                eval(
                    "(lambda *a, **kw: args.extend(a) or kwargs.update(kw))"+line,
                    {'args': args, 'kwargs': kwargs}
                )
                t = asyncio.create_task(self.call_one(cell, *args, **kwargs))
                self.last_magic = t
                self.magic_history.append(t)
                
            @register_line_cell_magic(f'{self_name}.call_all')
            def call_all(line, cell):
                args, kwargs = [], {}
                eval(
                    "(lambda *a, **kw: args.extend(a) or kwargs.update(kw))"+line,
                    {'args': args, 'kwargs': kwargs}
                )
                t = asyncio.create_task(self.call_all(cell, *args, **kwargs))
                self.last_magic = t
                self.magic_history.append(t)
                
            @register_line_cell_magic(f'{self_name}.call_map')
            def call_map(line, cell):
                args, kwargs = [], {}
                eval(
                    "(lambda *a, **kw: args.extend(a) or kwargs.update(kw))"+line,
                    {'args': args, 'kwargs': kwargs}
                )
                t = asyncio.create_task(self.call_map(cell, *args, **kwargs))
                self.last_magic = t
                self.magic_history.append(t)
                
        asyncio.create_task(register_line_magics())

    async def call_one(self, code, inputs=None, output=None, instance=None):
        if instance is None:
            instance = self.instances.popleft()
            self.instances.append(instance)
        if output:
            return await instance.execute(code, inputs)[output]
        return await instance.execute(code, inputs)
    
    async def call_all(self, code, inputs=None, output=None):
        await asyncio.gather(*[self.call_one(code, inputs, output, i) for i in self.instances])
    
    async def call_map(self, code, variable_name, iterable, inputs=None, output=None):
        tasks = []
        for item in iterable:
            item_inputs = (inputs or {}).copy()
            item_inputs[variable_name] = item
            tasks.append(self.call_one(code, item_inputs, output))
        return await asyncio.gather(*tasks)
