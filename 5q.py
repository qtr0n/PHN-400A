from utility import *
import matplotlib.pyplot as plt
import numpy as np

# Perform weight-1 Pauli correction according to the syndromes of four stabilizers.
def correctErrorsUsingSyndromes(errors, syndromes): 
  if syndromes == [0,0,0,0]: 
    pass
  elif syndromes == [0,0,0,1]: 
    errors.x ^= 1<<0
  elif syndromes == [1,0,1,1]: 
    errors.x ^= 1<<0
    errors.z ^= 1<<0
  elif syndromes == [1,0,1,0]: 
    errors.z ^= 1<<0
  elif syndromes == [1,0,0,0]: 
    errors.x ^= 1<<1
  elif syndromes == [1,1,0,1]: 
    errors.x ^= 1<<1
    errors.z ^= 1<<1
  elif syndromes == [0,1,0,1]: 
    errors.z ^= 1<<1
  elif syndromes == [1,1,0,0]: 
    errors.x ^= 1<<2
  elif syndromes == [1,1,1,0]: 
    errors.x ^= 1<<2
    errors.z ^= 1<<2
  elif syndromes == [0,0,1,0]: 
    errors.z ^= 1<<2
  elif syndromes == [0,1,1,0]: 
    errors.x ^= 1<<3
  elif syndromes == [1,1,1,1]: 
    errors.x ^= 1<<3
    errors.z ^= 1<<3
  elif syndromes == [1,0,0,1]: 
    errors.z ^= 1<<3
  elif syndromes == [0,0,1,1]: 
    errors.x ^= 1<<4
  elif syndromes == [0,1,1,1]: 
    errors.x ^= 1<<4
    errors.z ^= 1<<4
  elif syndromes == [0,1,0,0]: 
    errors.z ^= 1<<4

def extractSyndromes(errors, errorRates): 
  syndromes = [0 for i in range(4)]
  for j in range(4): 
    prepZ(5, errors, errorRates)
    dualcz(j%5, 5, errors, errorRates)
    cnot((j+1)%5, 5, errors, errorRates)
    cnot((j+2)%5, 5, errors, errorRates)
    dualcz((j+3)%5, 5, errors, errorRates)
    syndromes[j] = measZ(5, errors, errorRates)
  return syndromes

def prepCat(errors, errorRates, verbose):
  z=1
  while(z):
    prepX(5, errors, errorRates)
    prepZ(6, errors, errorRates)
    prepZ(7, errors, errorRates)
    prepZ(8, errors, errorRates)
    cnot(5, 6, errors, errorRates)
    cnot(5, 7, errors, errorRates)
    cnot(5, 8, errors, errorRates)
    prepZ(9, errors, errorRates)
    cnot(5, 9, errors, errorRates)
    cnot(6, 9, errors, errorRates)
    z = measZ(9, errors, errorRates)
    #if z&verbose: print "cat fail"
    if z & verbose:
      print("cat fail")


def correctErrors(errors, errorRates, verbose=False): 
  for i in range(4):
    if verbose: 
      print("starting syndrome{}".format(i))
    prepCat(errors, errorRates, verbose)
    cnot(5, i%5, errors, errorRates)
    cz(6, (i+1)%5, errors, errorRates)
    cz(7, (i+2)%5, errors, errorRates)
    cnot(8, (i+3)%5, errors, errorRates)
    if (measX(5, errors, errorRates)^measX(6, errors, errorRates)^measX(7, errors, errorRates)^measX(8, errors, errorRates))==1:
      #if verbose: print "syndrome%d"%i
      if verbose:
        print("syndrome{}".format(i))
      syndromes = extractSyndromes(errors, errorRates)
      if verbose: 
        print(syndromes)
      correctErrorsUsingSyndromes(errors, syndromes)
      return 1
  return 0

def weight(errors):
  return bin((errors.x | errors.z) & ((1 << 5) - 1)).count("1")

def reduceError(errors): 
  stabilizers = [[(1<<0)+(1<<3),(1<<1)+(1<<2)], [(1<<1)+(1<<4),(1<<2)+(1<<3)], [(1<<2)+(1<<0),(1<<3)+(1<<4)], [(1<<3)+(1<<1),(1<<4)+(1<<0)]]
  bestErrors = Errors(errors.x, errors.z)
  bestWeight = weight(bestErrors)
  trialErrors = Errors(0, 0)
  for k in range(1, 1<<(len(stabilizers))):
    trialErrors.x = errors.x
    trialErrors.z = errors.z
    for digit in range(len(stabilizers)):
      if (k>>digit)&1: 
        trialErrors.x ^= stabilizers[digit][0]
        trialErrors.z ^= stabilizers[digit][1]
    if weight(trialErrors) < bestWeight: 
      bestErrors.x = trialErrors.x
      bestErrors.z = trialErrors.z
      bestWeight = weight(bestErrors)
  return bestErrors

array_failure = [0]*21

def simulateErrorCorrection(gamma, trials): 
  errors = Errors(0, 0)
  errorsCopy = Errors(0, 0)
  
  errorRates0 = ErrorRates(0, 0, 0)
  errorRates = ErrorRates((4/15.)*gamma, gamma, (4/15.)*gamma)
  
  failures = 0
  for k in range(trials): 
    correctErrors(errors, errorRates)
    errorsCopy.x = errors.x
    errorsCopy.z = errors.z
    correctErrors(errorsCopy, errorRates0)
    errorsCopy = reduceError(errorsCopy)
    if (errorsCopy.x & ((1<<5)-1)) or (errorsCopy.z & ((1<<5)-1)): 
      failures += 1
      errors.x = 0
      errors.z = 0
  print(failures)
  array_failure.append(failures)
  plt.plot(gamma,failures,marker='*')
  plt.xlabel('CNOT failure probability')
  plt.ylabel('Number of failures')

gammas = [10**(i/10.-4) for i in range(21)]
for i in range(10):
  print("gamma=10^({}/10-4), trials=10^6".format(i))
  simulateErrorCorrection(gammas[i], 10**4)

for i in range(11):
  #print "gamma=10^(%d/10-4), trials=10^6"% (i+10)
  print("gamma=10^({}/10-4), trials=10^6".format(i+10))
  simulateErrorCorrection(gammas[i+10], 10**4)

plt.show()
