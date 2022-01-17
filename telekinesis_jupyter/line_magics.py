import asyncio
from collections import deque

import telekinesis as tk

class RemoteKernels:
    def __init__(self, *instances, ipython=None, print_callback=print):
        self.instances = deque(instances)
        self.last_magic = None
        self.magic_history = []
        self.print_callback = print_callback
        if ipython:
            asyncio.create_task(self.register_line_magics(ipython))
        
    async def register_line_magics(self, ipython, self_name=None):
        self_name = self_name or [ k for k,v in ipython.ns_table['user_global'].items() if v is self][0]
        
        def call_one(line, cell):
            args, kwargs = [], {}
            eval(
                "(lambda *a, **kw: args.extend(a) or kwargs.update(kw))"+line,
                {**ipython.ns_table['user_global'], 'args': args, 'kwargs': kwargs}
            )
            t = asyncio.create_task(self.call_one(cell, *args, **kwargs))
            self.last_magic = t
            self.magic_history.append(t)
            
        def call_all(line, cell):
            args, kwargs = [], {}
            eval(
                "(lambda *a, **kw: args.extend(a) or kwargs.update(kw))"+line,
                {**ipython.ns_table['user_global'], 'args': args, 'kwargs': kwargs}
            )
            t = asyncio.create_task(self.call_all(cell, *args, **kwargs))
            self.last_magic = t
            self.magic_history.append(t)
            
        def call_map(line, cell):
            args, kwargs = [], {}
            eval(
                "(lambda *a, **kw: args.extend(a) or kwargs.update(kw))"+line,
                {**ipython.ns_table['user_global'], 'args': args, 'kwargs': kwargs}
            )
            t = asyncio.create_task(self.call_map(cell, *args, **kwargs))
            self.last_magic = t
            self.magic_history.append(t)

        def inject_code(line, cell):
            args, kwargs = [], {}
            f_name, *rest = line.split(' ')
            eval(
                "(lambda *a, **kw: args.extend(a) or kwargs.update(kw))"+' '.join(rest),
                {**ipython.ns_table['user_global'], 'args': args, 'kwargs': kwargs}
            )
            f = ipython.ns_table['user_global'].items()[f_name]
            if isinstance(f, tk.Telekinesis):
                t = asyncio.create_task(f(cell, *args, **kwargs)._execute())
            elif not asyncio.iscoroutine(f):
                return f(cell, *args, **kwargs)
            else:
                t = asyncio.create_task(f(cell, *args, **kwargs))
            self.last_magic = t
            self.magic_history.append(t)

        ipython.register_magic_function(call_one, 'cell', f'{self_name}.call_one')
        ipython.register_magic_function(call_all, 'cell', f'{self_name}.call_all')
        ipython.register_magic_function(call_map, 'cell', f'{self_name}.call_map')
        ipython.register_magic_function(inject_code, 'cell', f'{self_name}.inject_code')

    async def call_one(self, code, inputs=None, output=None, instance=None, scope=None, print_callback=None):
        if instance is None:
            instance = self.instances.popleft()
            self.instances.append(instance)
        scope = scope or instance._session.instance_id
        print_callback = print_callback or self.print_callback
        if output:
            return await instance.execute(code, inputs, scope=scope, print_callback=print_callback)[output]
        return await instance.execute(code, inputs, scope=scope, print_callback=print_callback)
    
    async def call_all(self, code, inputs=None, output=None, scope=None, print_callback=None):
        return await asyncio.gather(*[self.call_one(code, inputs, output, i, scope, print_callback) for i in self.instances])
    
    async def call_map(self, code, variable_name, iterable, inputs=None, output=None, scope=None, print_callback=None):
        tasks = []
        for item in iterable:
            item_inputs = (inputs or {}).copy()
            item_inputs[variable_name] = item
            tasks.append(self.call_one(code, item_inputs, output, None, scope, print_callback))
        return await asyncio.gather(*tasks)

