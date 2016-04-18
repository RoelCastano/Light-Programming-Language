import operator
from light_semantic_controller import *
from memory import *

class MemoryHandler:
	# Global and local memory declarations
	global_size = len(FunctionTable.function_dict['program'].vars)

	# Global Memory
	const_vars = FunctionTable.flipped_constant_dict()
	heap = Memory(global_size, FunctionTable.function_dict['program'].var_quantities)

	# Local Memory, stores Memory objects
	stack = Stack()
	mem_to_push = 90

	__shared_state = {}
	def __init__(cls):
		cls.__dict__ = cls.__shared_state

	@classmethod
	def init_class_vars(cls):
		cls.global_size = len(FunctionTable.function_dict['program'].vars)
		cls.const_vars = FunctionTable.flipped_constant_dict()
		cls.heap = Memory(cls.global_size, FunctionTable.function_dict['program'].var_quantities)
		cls.stack = Stack()
		cls.mem_to_push = None

	@classmethod
	def binary_operator(cls, quad):
		left_op = cls.get_address_value(quad.left_operand)
		right_op = cls.get_address_value(quad.right_operand)
		result = execute_binary_operator(quad.operator, left_op, right_op)
		cls.set_address_value(quad.result, result)

	@classmethod
	def execute_binary_operator(cls, val, x, y):
		ops = {

			0	: operator.add(x,y),
			1	: operator.sub(x,y),
			2	: operator.mul(x,y),
			3	: operator.div(x,y),
			4	: operator.lt(x,y),
			5	: operator.gt(x,y),
			6	: operator.le(x,y),
			7	: operator.ge(x,y),
			8	: operator.eq(x,y),
			9	: operator.ne(x,y),
		}
		return ops[val]

	@classmethod
	def assign_operator(cls, quad):
		from_value = cls.get_address_value(quad.left_operand)
		cls.set_address_value(quad.result, from_value)

	@classmethod
	def and_or_operator(cls, quad):
		left_op = cls.get_address_value(quad.left_operand)
		right_op = cls.get_address_value(quad.right_operand)
		if quad.operator == 10 :
			cls.set_address_value(quad.result, (left_op and right_op))
		elif quad.operator == 11 :
			cls.set_address_value(quad.result, (left_op or right_op))

	@classmethod
	def get_address_value(cls, addr):
		type = (addr // 1000) # integer division
		relative_address = addr - type
		# use heap for search if addr is negative, else the current local mem
		if addr >= 14000:
			return cls.const_vars[addr]
		elif addr < 0:
			return cls.heap.memory[type][abs(relative_address)]
		return cls.stack.peek().memory[type][relative_address]

	@classmethod
	def set_address_value(cls, addr, val):
		print addr
		type = (addr // 1000) # integer division
		relative_address = addr - type
		# use heap for search if addr is negative, else the current local mem
		if addr >= 14000:
			cls.const_vars[addr] = val
		elif addr < 0:
			print cls.heap.memory
			print "Access: [{}][{}] = {}".format(type, abs(relative_address), val)
			cls.heap.memory[type][abs(relative_address)] = val
		else:
			cls.stack.peek().memory[type][relative_address] = val

	@classmethod
	def era_operator(cls, quad):
		func_name = quad.left_operand
		func = FunctionTable.function_dict[func_name]
		mem_to_push = Memory(len(func.vars), func.var_quantities) 
		print "> Created new memory for '{}': {}".format(func_name, mem_to_push.memory)

	