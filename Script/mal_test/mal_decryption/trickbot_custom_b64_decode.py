import base64
import string

enc_data = ["JXuiJXkHC3nuNMIWNXnuVSzYJXDk", "rmAiJXugRxniV0", "rmAHNxsgRxig", "JmAHRxiQrMsnRxDPsQ", "rMbuNxuupxiQRxbgN8", "Nmiipd4iCxnuNoiQRxbgN8", "VS4xrmbkpMiQRxbgN8", "rm0YJMnnCSFlRxniV0", "JmAHRxiQrMsnRxDPsQ", "JmAHRxiQREbf", "rM4iNE8YNMc", "VSVSRxqnsmuOsmFYJM/HC3nlNXO", "RSAZJMiY", "RXiQ", "RSFuVQ", "RS4ipd8", "R9DxNSFkJm8DVohwV0", "pxhYREbQJMqBJmh9RxDPsQ", "JXFZRxIfVmbiJm8YNSFE", "JfnfJmFPJMbqsoIlsMnOCxIZRxDPsQ", "son9JxQkz5nqJXhQCxDOsMbORxniV0", "CSAuN5n+NEbfN3n9NSFfCPnYsm8", "Jx4YCPnuV0", "Jx4YCPnfp8", "Jx4YCPnlNQ", "Jx4YCPnHN8", "Jx4YCPnZrMna", "Jx4YCPnYV8", "Jx4YCPnQCxT", "Jfq+NEzYCXc", "CEhYso/Zz9e", "NxDOeo/HCS4is0", "voqgsdhZsMbgNxsHs9w2v3DkNX4qNohlNXnxrMCy", "F10wNItizL4ZM3hZV8", "sEFisMFqsxsiCt", "4XhOcoIPsMnO5MnxNPAiCEFgCt", "edVgCxkHNxC", "cqi1h6hb", "hXiYsoDSCPA1smFXsmetzl0QzQ", "FmzYFmz", "1ohuVxhLCxiOrMbuNIbiJS4HNXw", "cdFgJXh9CPABJmztJxhiNfAxrMnHCXuis0B", "cOiK5t", "4MnOsmFLCxiOrMbuNIbiJS4HNXw", "vIh9smFFsLw", "coIPJMOtz0", "R5OiCPOkL8Bb3t", "8X/gCXheJMn+Noc", "cXiENxIZ1XF2sMbO8Mn+hXIHV0", "41Btzdtip3AAKf0Qp3hQ", "FmztFmztcq0iV8", "1oDus6/HJEFuCEim", "FmcYFmcYFmcYFmc", "v3DzNXVgNi4PrMVEsmey3t", "8SFiJm4ieIH8eosurM/is0", "4Ohc", "cdFgJXh9CPASJmztVMnZNXI+sM8", "FmciV5hqRt", "v3D8CxiYJXiQJMQy3lQgcdFHNxbHCoIZC9wGvIbiVd4HNxV9vtBT1mhZVoiQNohFNEbOJMnlsmb8NX/HJS+y5MVYNSFi1xhSv3DbVM/OrmAZsciYCS4uNxbiCqAgNoilp1wGv64HCXIZNoDScS4uCE4Fs+DY8xIOVohPrMh9vxsuNdbiv3D6rmbuNo/gVqbOJmFO5MsvN+FuVd4iCxiiC9wGvIbONSAFs+VgrMnE1Xn3Jm4OsmFHsmzyVdFqs1QgcS4gC6ix4XDHNxVvN+FuVd4iCxiiC9wGv6IZNoDS5oIPsI4iCxqHNxIOs1nOCEhiv3DANo/gVOuuCx4csmFkrMnuVocy3l/1VoIPVIVBsMnAVxIHNoIfNocyVdFqs1QgcS4uCE4mrohY8msurM/uJx/ivtBTcEhY1XnZpcix1xhOVXDPrOIXJMiZJMFZs1nxJM/9s1QgcEhY1XnZpcix1xhOVXDPrOIXJMiZJMFZs1wG31/Fso/icXhOVoiYsSzy3t+FvIbONSAvN+i+NohINx8yVdFqs1QgcS4gC6DY5M4ZschYsLwG38+Tcxh9VoIPV6DY5M4Zs1nxJM/9s1Qgcxh9VoIPV6DY5M4Zs1wG31Qg5M4ZshbiVd4HNxV9vtBT8M/ZNSV1VoIPV6DY4ohkJMn+vE4PVMcTROIZNoDScS4uCE4vN+4iNMIYsLwGv6hYJMFZsM8yVdFqs1Qg4MnuJx/isLwGv6uHso4iNlnxJM/9s1Qg5oi+sohYvtBTcEhY1XnZpcix5M4Zs1nxJM/9s1QgcEhY1XnZpcix5M4Zs1wGvIVurXhcNqFqNlnxJM/9s1QghXIash4gcEhYvtBT4muiJShOrMDYhoiksc/HNMiOviAczIzTROhwsMbqVoigNi4HNMhzrMqHVLwGvIAPrMDPrm4nvlJTRqAPrMDPrm4nvtBTRqbiVd4HNxV9vtBT8MbOrMDYCPALNXnOsmuOv5FAVm4BNSefvtBT4muiJ9wG31/LNXqkJMn+vt", "hXiYsoDSCP0S", "hMnaNxDSNt", "VxhPRE4wV0", "4X/gJxIZm0", "sxIHNoh+", "4xiPCS8", "v6FgNS4cCxiEsXhPvtBT4MnuJx/isLnOCEhiv3DINxIfNoh+vtB", "b10", "FmzgFmzgblzgFmzgFmzgFmzgFmzg", "hXiYsoDSCP0w", "CXuZVXIQr8", "m3B", "5MnXJM/Hs3AQJmFuNmztJXDqNE8", "FmztFmz", "hXIYVIFiNohuCXc", "FmzYFmzYFmzYFmz", "F10/bx/ZM3cQz1sZNIt", "vLDwNMQtVxhPCXigNlOfz5wQefAiNxbgsoiYs9Ofhh4oR16XelTyvI4uCXZtVxhPCXigNlOfz5wPefAwNM/YC9Ofrd4OCLBgRSblrohkJmzYNMilCxD9NXsORxbgN5DSrMn+NSV9R9eQzL8gzLegNMiORS4uCXZfvtBTcxhErmbOCxIOrMDY5MnxN9wGvIsiCEbHNXwyz5w/Rl6TRqsiCEbHNXwy3l/AVm4BNSey5o4+e6iYsxTTROIqVougClwGv64iCXbPrmAOrMDYv+u+s3AHNxsgeoIQCo/HJXIOrMDYeosgCfASrMn+NSV9eLQg4oh9JSFHCd4HNXwy3l/hc++ymIVHNfAeso8t5MnxN9QghhFFvtBTRqFisXi9VdFuVoigN+iYsxTy3l/cCxiEsXhPC9wG", "RPh9RPh9R9e9RPhqRQ", "hXiYz9etsmFPNSe", "RPh9RPh9R9cgFmzg", "NxDYJMqi", "FmztCq4uCE8", "sohZsm4i", "FmziCQ", "8O+tsxIHNoh+R30Qp3hw", "JXnC", "CxhZNXI+FM8", "4muHVIAPNXbiCSz", "cEhYe68tsxIHNoh+", "1oDus3AONPAbeosurM/is0", "v3DIpohlvtBTROIlVoigNEzy3lQghoI9r9wG", "1MD+VM/ieoIZCxhusd+tVMnZNXI+sM8", "CxhZsMI9s8", "1+IcedbOJm4qCQ", "4LBB81Z74O67K9km43+B81Z74O67K9k385+B81Z74O67K9k1M5+B81Z74O67K9k58P+", "CXhOVoiYsSzYrMnH", "RE4kC0", "5MnHVoiuNoiWscbPrm4HJXIZcXhlVoigNt", "smul", "1MD+VM/ieouuCPAuNdFiJM4neoFisMwtNoDusoh+", "c6D1h0", "RPh9RPh9R96gFmzg", "mobks3nipoc", "e3hqe3hqe3hqe3hq", "FmzgFmzgbl8gFmzgFmzgFmzg", "cXiENxIOVmFi1ohYsS4B", "cS4uCE8tsxIHNoh+", "hXiYsoDSCP0/z3A1smFXsme", "sxiZs8", "z3wQRl0Yz0", "RPh9RPh9R9eqRPh9RQ", "soIOJ8", "1xTtCoIPJMq9", "rMnxNQ", "hXiYsoDSCPA1smFXsmetzl0/zfA5zt", "sMwk4cnC", "hq414XhO8MbOrmsi8XDYCXDZshbiCSbHNXnFs0", "NmhOJMnO", "CxhECSsPz9e", "hXiYsoDSCPA1smFXsmetzl0QK3A5zt", "rXhPNxhZz9eYso/Z", "8XDYVdFgN3AxJMiZsM8", "hXiYsoDSCP0PzL0Q", "rmb+r8", "CEhYso/Zz9eYsmuie0", "RE4wV0", "v3DLNXqkJMn+vt", "RPh9RPh9R90gFmzgFmzgFmzgFmzgFmzg", "v3D3NXDOhdFHsXViClwG", "Noi9Voh+", "hXIHV6sgCibHNxVZscDfrxhlV0", "8XDYVohYV3qcpmAiKfAkVM/OrmAuCE8gsxDPN5q+Jm4uKPAfNShYsoIPp1OiCQOG8XDYVohYV3qzsMnEVotWe3h+L8Bb3t", "JX/HsMnOeoi9eoFiroiYs3AK8h8", "cXh6sMFqsqAPrmsHNohEs8", "v3DhCXhP5M8y", "hXiYsoDSCPAJc0", "pLJO", "cXhcJXF8CxiXrM/isXc", "RPh9RPh9R96ORPh9RPh9R90g", "4muiJShOs5AxCxDkedh9sme", "5o4+eoiYsxTtJmAQNoilJm4HNXw", "4muiJShOs5AxCxDkedbnCS4iN8", "hMnuJx/ied4geo/gJM8tNMD+VM/ieosPNXOtCXhPVxhP", "RPh9RPh9R96QRPh9RPh9RPhqRQ", "4xiYs3A8eosurM/is0", "REFiNoDl", "hq414MnqNMhPJm4icXh9CXigNEbA", "z16Qbt", "hXiYsoDSCP0/z0", "4cb6cOIUcLzwb0", "hmFZ4mblJmAihQ", "cxhErmbOsmetCPAxJMiZsM8ZeLAwFmt", "e3DLeob9JSFHCd8t", "4ohlNX4iedAuCxIkbl8tsmFPNSe", "C6ice6nh16Q", "vIFqN+/iVxhZv+uHsXuiCS4AVxIHNoIfNocTRqFqN+/iVxhZvtBT4SFgVmAFsLnKh3AAhh4e1qFFhIiCcqi1h6hbv3DdCxDqC6i+vtBT1oDENXncpmAiv+iYVohPJMbOrmsihoDasMwTRO/gsXDYhdiQs1wG", "smuQNoDPsmeYsmui", "hXiYsoDSCPA1smFXsmetzl0/zt", "VXiYCS4uzI/+sMsuVM/O", "JXq+Rxhws8", "cxh9sm4IVxhYV0", "1MD+VM/ieoi9eongV3AXJM/Hs0", "JXDYVdFgN0", "CS4uCE8", "mou+s6iYsxT", "cxhErmbOsmetV5AxJMiZsM8ZeLAwFmt", "v6/gsXDYhdFHsXViClwGv6hYJMFZsM8yVdFqs1Qg4MnuJx/isLwG", "JX/HsMnOeoi9eongV3AfsMuHNx8t1+Ic", "hXiYsoDSCPA1smFXsmetzl0QK0", "h+h5cQ", "C6iceobgNxniJS8tsxIHNoh+R30Qp3hw", "v3DLNXqkJMn+vtBT8mFEVMqiNE49vt", "F10PM0", "4cbLcIh316iL8+/v8t", "8SFiJm4iedukN3AxJMiZsM8", "8SFiJm4iedukNLetsxIHNoh+", "C6ice6ViV6sgNo4iCfAxJMiZsM8ZeLAwFmt", "v6/gsXDYhdiQs1nFNE4iCxIlVoiXsh4grXhYv3DzNXVgNi4nCocy3l/5VMnzsmsiNLnzsMI9VIAPrmsHNohEs1QgcEhY1ohXsMQy", "cIFv1hAc", "pLtX", "R5OiCQOG8XDYVohYV3q6rmbQNSbHVoigNlBtsxDPN5q+Jm4uKPAYJMqiv5eicPeb3tOG", "hq414EFiscqiNMDPp8", "hXiYsoDSCPAMrmbOJ8", "v3DACxVqNMhYVdzy3t", "VS49JmAHz9e", "mdbXJXugCS8Ysmui", "1oDus3AONPA8eosurM/is0", "4XhOcdFgJOI+sdFiCSz", "CoIOr0", "46n18+Q", "cPO/R1ckz1t", "hq41cmhiCEihCXhPhoDasMw", "VoqQ", "VmbiCt", "v3DcCxiEsXhPC9wGvIAPrMnlrmAuNdzy3l/8CxiYJXiQJMQtrM8De+IqVougCfey3t", "RQ", "hXiYsoDSCP0wRl6", "R5OkR5Ok8xDqNx4uCE+izLuJ", "JShPN3TSRlCORl0", "1oIqNxbBeIh14hetsxIHNoh+", "1MD+VM/icmhiCE+", "hhbIc+hKhfn+NoQ", "1O/I8hhcz9eYso/Z", "hhbIclzPRx4ZN0", "NxbPpmAORx4ZN0", "cOuzhOI855n+NoQ", "hOiK5I4cc3n+NoQ", "cOuI16Q9zfn+NoQ", "NE4+NoQYso/Z", "JxbPpmAORx4ZN0", "hqzPm9zPRx4ZN0", "8qFscI89zfn+NoQ", "5hAe1IAAc6+Y46/z", "NX/iz9eYso/Z", "8c4M8hAFz9eYso/Z"]
std_base64chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"
custom          = ""

if len(std_base64chars) == len(custom):
	for data in enc_data:
		fixed_data = data.translate(str.maketrans(custom, std_base64chars)).encode()
		if len(fixed_data) % 4 == 0:
			decoded = base64.b64decode(fixed_data).decode()
		else:
			fixed_data = fixed_data + b"=" * (len(fixed_data) % 4)
			decoded = base64.b64decode(fixed_data).decode()
		print(f"{data}: {decoded}")
else:
	print("Invalid b64 key!!")

# JXuiJXkHC3nuNMIWNXnuVSzYJXDk: checkip.amazonaws.com
# rmAiJXugRxniV0: ipecho.net
# rmAHNxsgRxig: ipinfo.io
# JmAHRxiQrMsnRxDPsQ: api.ipify.org
# rMbuNxuupxiQRxbgN8: icanhazip.com
# Nmiipd4iCxnuNoiQRxbgN8: myexternalip.com
# VS4xrmbkpMiQRxbgN8: wtfismyip.com
# rm0YJMnnCSFlRxniV0: ip.anysrc.net
# JmAHRxiQrMsnRxDPsQ: api.ipify.org
# JmAHRxiQREbf: api.ip.sb
# rM4iNE8YNMc: ident.me
# VSVSRxqnsmuOsmFYJM/HC3nlNXO: www.myexternalip.com
# RSAZJMiY: /plain
# RXiQ: /ip
# RSFuVQ: /raw
# RS4ipd8: /text
# R9DxNSFkJm8DVohwV0: /?format=text
# pxhYREbQJMqBJmh9RxDPsQ: zen.spamhaus.org
# JXFZRxIfVmbiJm8YNSFE: cbl.abuseat.org
# JfnfJmFPJMbqsoIlsMnOCxIZRxDPsQ: b.barracudacentral.org
# son9JxQkz5nqJXhQCxDOsMbORxniV0: dnsbl-1.uceprotect.net
# CSAuN5n+NEbfN3n9NSFfCPnYsm8: spam.dnsbl.sorbs.net
# Jx4YCPnuV0: bdns.at
# Jx4YCPnfp8: bdns.by
# Jx4YCPnlNQ: bdns.co
# Jx4YCPnHN8: bdns.im
# Jx4YCPnZrMna: bdns.link
# Jx4YCPnYV8: bdns.nu
# Jx4YCPnQCxT: bdns.pro
# Jfq+NEzYCXc: b-dns.se
# CEhYso/Zz9e: rundll32
# NxDOeo/HCS4is0: not listed
# voqgsdhZsMbgNxsHs9w2v3DkNX4qNohlNXnxrMCy: <moduleconfig>*</moduleconfig>
# F10wNItizL4ZM3hZV8: %08lX%04lX%lu
# sEFisMFqsxsiCt: freebuffer
# 4XhOcoIPsMnO5MnxNPAiCEFgCt: GetParentInfo error
# edVgCxkHNxC:  working
# cqi1h6hb: SYSTEM
# hXiYsoDSCPA1smFXsmetzl0QzQ: Windows Server 2003
# FmzYFmz: %s.%s
# 1ohuVxhLCxiOrMbuNIbiJS4HNXw: LeaveCriticalSection
# cdFgJXh9CPABJmztJxhiNfAxrMnHCXuis0B: Process has been finished

# cOiK5t: SINJ
# 4MnOsmFLCxiOrMbuNIbiJS4HNXw: EnterCriticalSection
# vIh9smFFsLw: <UserId>
# coIPJMOtz0: Param 0
# R5OiCPOkL8Bb3t: --%s--


# 8X/gCXheJMn+Noc: CloseHandle
# cXiENxIZ1XF2sMbO8Mn+hXIHV0: SignalObjectAndWait
# 41Btzdtip3AAKf0Qp3hQ: E: 0x%x A: 0x%p
# FmztFmztcq0iV8: %s %s SP%u
# 1oDus6/HJEFuCEim: LoadLibraryW
# FmcYFmcYFmcYFmc: %u.%u.%u.%u
# v3DzNXVgNi4PrMVEsmey3t: </LogonTrigger>

# 8SFiJm4ieIH8eosurM/is0: Create ZP failed
# 4Ohc: GET
# cdFgJXh9CPASJmztVMnZNXI+sM8: Process was unloaded
# FmciV5hqRt: %u%u%u.
# v3D8CxiYJXiQJMQy3lQgcdFHNxbHCoIZC9wGvIbiVd4HNxV9vtBT1mhZVoiQNohFNEbOJMnlsmb8NX/H
# JS+y5MVYNSFi1xhSv3DbVM/OrmAZsciYCS4uNxbiCqAgNoilp1wGv64HCXIZNoDScS4uCE4Fs+DY8xIO
# VohPrMh9vxsuNdbiv3D6rmbuNo/gVqbOJmFO5MsvN+FuVd4iCxiiC9wGvIbONSAFs+VgrMnE1Xn3Jm4O
# smFHsmzyVdFqs1QgcS4gC6ix4XDHNxVvN+FuVd4iCxiiC9wGv6IZNoDS5oIPsI4iCxqHNxIOs1nOCEhi
# v3DANo/gVOuuCx4csmFkrMnuVocy3l/1VoIPVIVBsMnAVxIHNoIfNocyVdFqs1QgcS4uCE4mrohY8msu
# rM/uJx/ivtBTcEhY1XnZpcix1xhOVXDPrOIXJMiZJMFZs1nxJM/9s1QgcEhY1XnZpcix1xhOVXDPrOIX
# JMiZJMFZs1wG31/Fso/icXhOVoiYsSzy3t+FvIbONSAvN+i+NohINx8yVdFqs1QgcS4gC6DY5M4ZschY
# sLwG38+Tcxh9VoIPV6DY5M4Zs1nxJM/9s1Qgcxh9VoIPV6DY5M4Zs1wG31Qg5M4ZshbiVd4HNxV9vtBT
# 8M/ZNSV1VoIPV6DY4ohkJMn+vE4PVMcTROIZNoDScS4uCE4vN+4iNMIYsLwGv6hYJMFZsM8yVdFqs1Qg
# 4MnuJx/isLwGv6uHso4iNlnxJM/9s1Qg5oi+sohYvtBTcEhY1XnZpcix5M4Zs1nxJM/9s1QgcEhY1XnZ
# pcix5M4Zs1wGvIVurXhcNqFqNlnxJM/9s1QghXIash4gcEhYvtBT4muiJShOrMDYhoiksc/HNMiOviAc
# zIzTROhwsMbqVoigNi4HNMhzrMqHVLwGvIAPrMDPrm4nvlJTRqAPrMDPrm4nvtBTRqbiVd4HNxV9vtBT
# 8MbOrMDYCPALNXnOsmuOv5FAVm4BNSefvtBT4muiJ9wG31/LNXqkJMn+vt: </Principal>
# </Principals>
# <Settings>
# <MultipleInstancesPolicy>IgnoreNew</MultipleInstancesPolicy>
# <DisallowStartIfOnBatteries>false</DisallowStartIfOnBatteries>
# <StopIfGoingOnBatteries>true</StopIfGoingOnBatteries>
# <AllowHardTerminate>true</AllowHardTerminate>
# <StartWhenAvailable>true</StartWhenAvailable>
# <RunOnlyIfNetworkAvailable>false</RunOnlyIfNetworkAvailable>
#         <IdleSettings>
#                 <StopOnIdleEnd>true</StopOnIdleEnd>
#                 <RestartOnIdle>false</RestartOnIdle>
#         </IdleSettings>
# <AllowStartOnDemand>true</AllowStartOnDemand>
# <Enabled>true</Enabled>
# <Hidden>false</Hidden>
# <RunOnlyIfIdle>false</RunOnlyIfIdle>
# <WakeToRun>false</WakeToRun>
# <ExecutionTimeLimit>PT0S</ExecutionTimeLimit>
# <Priority>6</Priority>
# </Settings>
# <Actions Context="Author">
# <Exec>
#         <Command>
# hXiYsoDSCP0S: Windows 7
# hMnaNxDSNt: Unknown
# VxhPRE4wV0: ver.txt
# 4X/gJxIZm0: Global\
# sxIHNoh+: failed
# 4xiPCS8: First
# v6FgNS4cCxiEsXhPvtBT4MnuJx/isLnOCEhiv3DINxIfNoh+vtB: <BootTrigger>
# <Enabled>true</Enabled>

# b10: 50
# FmzgFmzgblzgFmzgFmzgFmzgFmzg: %s/%s/63/%s/%s/%s/%s/
# hXiYsoDSCP0w: Windows 8
# CXuZVXIQr8: shlwapi
# m3B: \*
# 5MnXJM/Hs3AQJmFuNmztJXDqNE8: Invalid params count
# FmztFmz: %s %s
# hXIYVIFiNohuCXc: WantRelease
# FmzYFmzYFmzYFmz: %s.%s.%s.%s
# F10/bx/ZM3cQz1sZNIt: %016llX%016llX
# vLDwNMQtVxhPCXigNlOfz5wQefAiNxbgsoiYs9Ofhh4oR16XelTyvI4uCXZtVxhPCXigNlOfz5wPefAw
# NM/YC9Ofrd4OCLBgRSblrohkJmzYNMilCxD9NXsORxbgN5DSrMn+NSV9R9eQzL8gzLegNMiORS4uCXZf
# vtBTcxhErmbOCxIOrMDY5MnxN9wGvIsiCEbHNXwyz5w/Rl6TRqsiCEbHNXwy3l/AVm4BNSey5o4+e6iY
# sxTTROIqVougClwGv64iCXbPrmAOrMDYv+u+s3AHNxsgeoIQCo/HJXIOrMDYeosgCfASrMn+NSV9eLQg
# 4oh9JSFHCd4HNXwy3l/hc++ymIVHNfAeso8t5MnxN9QghhFFvtBTRqFisXi9VdFuVoigN+iYsxTy3l/c
# CxiEsXhPC9wG: <?xml version="1.0" encoding="UTF-16"?><Task version="1.2" xmlns="
# http://schemas.microsoft.com/windows/2004/02/mit/task">
# <RegistrationInfo>
# <Version>1.1.1</Version>
# <Author>Hdd Info</Author>
# <Description>Hdd info application for windows </Description>
# <URI>\Win Hdd Info</URI>
# </RegistrationInfo>
# <Triggers>

# RPh9RPh9R9e9RPhqRQ: /%s/%s/23/%u/
# hXiYz9etsmFPNSe: Win32 error
# RPh9RPh9R9cgFmzg: /%s/%s/5/%s/
# NxDYJMqi: noname
# FmztCq4uCE8: %s sTart
# sohZsm4i: delete
# FmziCQ: %s%s
# 8O+tsxIHNoh+R30Qp3hw: CI failed, 0x%x
# JXnC: cn\
# CxhZNXI+FM8: reload%d
# 4muHVIAPNXbiCSz: ExitProcess
# cEhYe68tsxIHNoh+: Run D failed
# 1oDus3AONPAbeosurM/is0: Load to M failed
# v3DIpohlvtBTROIlVoigNEzy3lQghoI9r9wG: </Exec>
# </Actions>
# </Task>

# 1MD+VM/ieoIZCxhusd+tVMnZNXI+sM8: Module already unloaded
# CxhZsMI9s8: release
# 1+IcedbOJm4qCQ: NAT status
# 4LBB81Z74O67K9km43+B81Z74O67K9k385+B81Z74O67K9k1M5+B81Z74O67K9k58P+: D:(A;;GA;;;
# WD)(A;;GA;;;BA)(A;;GA;;;SY)(A;;GA;;;RC)
# CXhOVoiYsSzYrMnH: settings.ini
# RE4kC0: .tmp
# 5MnHVoiuNoiWscbPrm4HJXIZcXhlVoigNt: InitializeCriticalSection
# smul: exc
# 1MD+VM/ieouuCPAuNdFiJM4neoFisMwtNoDusoh+: Module has already been loaded
# c6D1h0: POST
# RPh9RPh9R96gFmzg: /%s/%s/1/%s/
# mobks3nipoc: \cmd.exe
# e3hqe3hqe3hqe3hq:  %u %u %u %u
# FmzgFmzgbl8gFmzgFmzgFmzg: %s/%s/64/%s/%s/%s/
# cXiENxIOVmFi1ohYsS4B: SignatureLength
# cS4uCE8tsxIHNoh+: Start failed
# hXiYsoDSCP0/z3A1smFXsme: Windows 10 Server
# sxiZs8: file
# z3wQRl0Yz0: 0.0.0.0
# RPh9RPh9R9eqRPh9RQ: /%s/%s/25/%s/
# soIOJ8: data
# 1xTtCoIPJMq9: No params
# rMnxNQ: info
# hXiYsoDSCPA1smFXsmetzl0/zfA5zt: Windows Server 2012 R2
# sMwk4cnC: en-EN\
# hq414XhO8MbOrmsi8XDYCXDZshbiCSbHNXnFs0: WTSGetActiveConsoleSessionId
# NmhOJMnO: mutant
# CxhECSsPz9e: regsvr32
# hXiYsoDSCPA1smFXsmetzl0QK3A5zt: Windows Server 2008 R2
# rXhPNxhZz9eYso/Z: kernel32.dll
# 8XDYVdFgN3AxJMiZsM8: Control failed
# hXiYsoDSCP0PzL0Q: Windows 2000
# rmb+r8: isdi
# CEhYso/Zz9eYsmuie0: rundll32.exe
# RE4wV0: .txt
# v3DLNXqkJMn+vt: </Command>
# RPh9RPh9R90gFmzgFmzgFmzgFmzgFmzg: /%s/%s/0/%s/%s/%s/%s/%s/
# v3D3NXDOhdFHsXViClwG: </BootTrigger>

# Noi9Voh+: listed
# hXIHV6sgCibHNxVZscDfrxhlV0: WaitForSingleObject
# 8XDYVohYV3qcpmAiKfAkVM/OrmAuCE8gsxDPN5q+Jm4uKPAfNShYsoIPp1OiCQOG8XDYVohYV3qzsMnE
# VotWe3h+L8Bb3t: Content-Type: multipart/form-data; boundary=%s
# Content-Length: %d


# JX/HsMnOeoi9eoFiroiYs3AK8h8: client is behind NAT
# cXh6sMFqsqAPrmsHNohEs8: SeDebugPrivilege
# v3DhCXhP5M8y: </UserId>
# hXiYsoDSCPAJc0: Windows XP
# pLJO: x64
# cXhcJXF8CxiXrM/isXc: SeTcbPrivilege
# RPh9RPh9R96ORPh9RPh9R90g: /%s/%s/14/%s/%s/0/
# 4muiJShOs5AxCxDkedh9sme: Execute from user
# 5o4+eoiYsxTtJmAQNoilJm4HNXw: Hdd info application
# 4muiJShOs5AxCxDkedbnCS4iN8: Execute from system
# hMnuJx/ied4geo/gJM8tNMD+VM/ieosPNXOtCXhPVxhP: Unable to load module from server
# RPh9RPh9R96QRPh9RPh9RPhqRQ: /%s/%s/10/%s/%s/%u/
# 4xiYs3A8eosurM/is0: Find P failed
# REFiNoDl: .reloc
# hq414MnqNMhPJm4icXh9CXigNEbA: WTSEnumerateSessionsA
# z16Qbt: 1106
# hXiYsoDSCP0/z0: Windows 10
# 4cb6cOIUcLzwb0: ECDSA_P384
# hmFZ4mblJmAihQ: UrlEscapeW
# cxhErmbOsmetCPAxJMiZsM8ZeLAwFmt: Register s failed, 0x%x
# e3DLeob9JSFHCd8t:  /C cscript
# 4ohlNX4iedAuCxIkbl8tsmFPNSe: Decode param64 error
# C6ice6nh16Q: pIT NULL
# vIFqN+/iVxhZv+uHsXuiCS4AVxIHNoIfNocTRqFqN+/iVxhZvtBT4SFgVmAFsLnKh3AAhh4e1qFFhIiC
# cqi1h6hbv3DdCxDqC6i+vtBT1oDENXncpmAiv+iYVohPJMbOrmsihoDasMwTRO/gsXDYhdiQs1wG: <R
# unLevel>HighestAvailable</RunLevel>
# <GroupId>NT AUTHORITY\SYSTEM</GroupId>
# <LogonType>InteractiveToken</LogonType>

# smuQNoDPsmeYsmui: explorer.exe
# hXiYsoDSCPA1smFXsmetzl0/zt: Windows Server 2012
# VXiYCS4uzI/+sMsuVM/O: winsta0\default
# JXq+Rxhws8: cmd.exe
# cxh9sm4IVxhYV0: ResetEvent
# 1MD+VM/ieoi9eongV3AXJM/Hs0: Module is not valid
# JXDYVdFgN0: control
# CS4uCE8: start
# mou+s6iYsxT: \hddInfo
# cxhErmbOsmetV5AxJMiZsM8ZeLAwFmt: Register u failed, 0x%x
# v6/gsXDYhdFHsXViClwGv6hYJMFZsM8yVdFqs1Qg4MnuJx/isLwG: <LogonTrigger>
# <Enabled>true</Enabled>

# JX/HsMnOeoi9eongV3AfsMuHNx8t1+Ic: client is not behind NAT
# hXiYsoDSCPA1smFXsmetzl0QK0: Windows Server 2008
# h+h5cQ: VERS
# C6iceobgNxniJS8tsxIHNoh+R30Qp3hw: pIT connect failed, 0x%x
# v3DLNXqkJMn+vtBT8mFEVMqiNE49vt: </Command>
# <Arguments>
# F10PM0: %02X
# 4cbLcIh316iL8+/v8t: ECCPUBLICBLOB
# 8SFiJm4iedukN3AxJMiZsM8: Create xml failed
# 8SFiJm4iedukNLetsxIHNoh+: Create xml2 failed
# C6ice6ViV6sgNo4iCfAxJMiZsM8ZeLAwFmt: pIT GetFolder failed, 0x%x
# v6/gsXDYhdiQs1nFNE4iCxIlVoiXsh4grXhYv3DzNXVgNi4nCocy3l/5VMnzsmsiNLnzsMI9VIAPrmsH
# NohEs1QgcEhY1ohXsMQy: <LogonType>InteractiveToken</LogonType>
# <RunLevel>LeastPrivilege</RunLevel>
# cIFv1hAc: PROMPT
# pLtX: x86
# R5OiCQOG8XDYVohYV3q6rmbQNSbHVoigNlBtsxDPN5q+Jm4uKPAYJMqiv5eicPeb3tOG: --%s
# Content-Disposition: form-data; name="%S"


# hq414EFiscqiNMDPp8: WTSFreeMemory
# hXiYsoDSCPAMrmbOJ8: Windows Vista
# v3DACxVqNMhYVdzy3t: </Arguments>

# VS49JmAHz9e: wtsapi32
# mdbXJXugCS8Ysmui: \svchost.exe
# 1oDus3AONPA8eosurM/is0: Load to P failed
# 4XhOcdFgJOI+sdFiCSz: GetProcAddress
# CoIOr0: path
# 46n18+Q: DNSBL
# cPO/R1ckz1t: S-1-5-18
# hq41cmhiCEihCXhPhoDasMw: WTSQueryUserToken
# VoqQ: tmp
# VmbiCt: user
# v3DcCxiEsXhPC9wGvIAPrMnlrmAuNdzy3l/8CxiYJXiQJMQtrM8De+IqVougCfey3t: </Triggers>
# <Principals>
# <Principal id="Author">

# RQ: /
# hXiYsoDSCP0wRl6: Windows 8.1
# R5OkR5Ok8xDqNx4uCE+izLuJ: ------Boundary%08X
# JShPN3TSRlCORl0: curl/7.74.0
# 1oIqNxbBeIh14hetsxIHNoh+: Launch USER failed
# 1MD+VM/icmhiCE+: ModuleQuery
# hhbIc+hKhfn+NoQ: USERENV.dll
# 1O/I8hhcz9eYso/Z: OLEAUT32.dll
# hhbIclzPRx4ZN0: USER32.dll
# NxbPpmAORx4ZN0: ncrypt.dll
# cOuzhOI855n+NoQ: SHLWAPI.dll
# hOiK5I4cc3n+NoQ: WINHTTP.dll
# cOuI16Q9zfn+NoQ: SHELL32.dll
# NE4+NoQYso/Z: ntdll.dll
# JxbPpmAORx4ZN0: bcrypt.dll
# hqzPm9zPRx4ZN0: WS2_32.dll
# 8qFscI89zfn+NoQ: CRYPT32.dll
# 5hAe1IAAc6+Y46/z: IPHLPAPI.DLL
# NX/iz9eYso/Z: ole32.dll
# 8c4M8hAFz9eYso/Z: ADVAPI32.dll