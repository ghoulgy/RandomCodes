cust_murmurhash_routine = toAddr(0x405650)

xrefs = getReferencesTo(cust_murmurhash_routine)

hash_arr = []

for xref in xrefs:
	callee = xref.getFromAddress()
	inst = getInstructionAt(callee)
	prev_inst = getInstructionBefore(inst)
	prev_addr= prev_inst.getAddress()
	mnemonic = prev_inst.getMnemonicString()

	if mnemonic == "PUSH":
		try:
			func_hash = prev_inst.getOpObjects(0)[0]
			hash_arr.append(func_hash)
			print "first: ", prev_addr, func_hash
			continue
		except: continue
	else:
		prev_inst_2 = getInstructionBefore(prev_inst)
		prev_addr_2 = prev_inst_2.getAddress()
		mnemonic_2 = prev_inst_2.getMnemonicString()
		if mnemonic_2 == "PUSH":
 			try:
				func_hash = prev_inst_2.getOpObjects(0)[0]
				hash_arr.append(func_hash)
				print "second: ", prev_addr_2, func_hash
				continue
			except: continue
		else:
			prev_inst_3 = getInstructionBefore(prev_inst_2)
			prev_addr_3 = prev_inst_3.getAddress()
			mnemonic_3 = prev_inst_3.getMnemonicString()
			if mnemonic_3 == "PUSH":
	 			try:
					func_hash = prev_inst_3.getOpObjects(0)[0]
					hash_arr.append(func_hash)
					print "third: ", prev_addr_3, func_hash
					continue
				except: continue
			else:
				prev_inst_4 = getInstructionBefore(prev_inst_3)
				prev_addr_4 = prev_inst_4.getAddress()
				mnemonic_4 = prev_inst_4.getMnemonicString()
				if mnemonic_4 == "PUSH":
		 			try:
						func_hash = prev_inst_4.getOpObjects(0)[0]
						hash_arr.append(func_hash)
						print "fourth: ", prev_addr_4, func_hash
						continue
					except: continue
				else:
					prev_inst_5 = getInstructionBefore(prev_inst_4)
					prev_inst_6 = getInstructionBefore(prev_inst_5)
					prev_addr_6 = prev_inst_6.getAddress()
					mnemonic_6 = prev_inst_6.getMnemonicString()
					if mnemonic_6 == "PUSH":
			 			try:
							func_hash = prev_inst_6.getOpObjects(0)[0]
							hash_arr.append(func_hash)
							print "sixth: ", prev_addr_6, func_hash
							continue
						except: continue
					else:
						prev_inst_7 = getInstructionBefore(prev_inst_6)
						prev_addr_7 = prev_inst_7.getAddress()
						mnemonic_7 = prev_inst_7.getMnemonicString()
						if mnemonic_7 == "PUSH":
				 			try:
								func_hash = prev_inst_7.getOpObjects(0)[0]
								hash_arr.append(func_hash)
								print "seventh: ", prev_addr_7, func_hash
								continue
							except: continue
						else:
							print "nope", inst.getAddress()
