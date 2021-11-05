import pandas as pd
import numpy as np

#dfList = pd.read_csv('list_boost.txt', sep='.', header=None)
#del dfList[9]
#eventSeries = dfList.stack().reset_index(drop=True)
#eventList = eventSeries.to_list()
OverlapEvents = np.array([])
UniqueEvents = np.array([])
fggEvents = np.array([])
with open("SR_Overlap_events.txt", 'r') as oEvents:
    for event in oEvents.readlines():
        OverlapEvents = np.append(OverlapEvents, [float(event.replace('\n',''))])
with open("SR_Unique_events.txt", 'r') as uEvents:
    for event in uEvents.readlines():
        UniqueEvents = np.append(UniqueEvents, [float(event.replace('\n',''))])
with open("fgg_events.txt", 'r') as fEvents:
    for event in fEvents.readlines():
        fggEvents = np.append(fggEvents, [float(event.replace('\n',''))])

#df = pd.read_pickle("/home/users/ian/HggAnalysisDev/MVAs/output/Overlap_testing.pkl").sort_values(by='event').reset_index(drop=True)
df = pd.read_pickle(
    "/home/users/azecchin/Analysis/HggAnalysisDev/Preselection/output/HHggbb_boosted_Presel_GenInfo_Test350Fatjet.pkl").sort_values(by='event').reset_index(drop=True)

dfOverlap = pd.DataFrame(columns=df.keys())
dfUnique = pd.DataFrame(columns=df.keys())
dfInc = pd.read_pickle(
    "/home/users/azecchin/Analysis/HggAnalysisDev/Preselection/output/HHggbb_boosted_Presel_GenInfo_TestLoop.pkl").sort_values(by='event').reset_index(drop=True)

repeats = np.array([])
nResolvedHgg = 0
nBoostedHgg = 0
boostedHgg = np.array([])
for i in range(len(df)):
    if i % 1000 == 0:
        print("Reached Event: {}".format(i))
    if df['event'][i] in repeats:
        continue
    else:
        repeats = np.append(repeats, [df['event'][i]])
    if df['process_id'][i] >= 0:
        continue
#    if df['mva_score'][i] < 0.975661:
#        continue

    if (df['Hbb_pt'][i] < 350) or (df['genBBfromH_delta_R'][i] > 0.8):
        nResolvedHgg += 1
    else:
        nBoostedHgg += 1
        boostedHgg = np.append(boostedHgg, [df['event'][i]])

    if df['event'][i] in OverlapEvents:
        dfOverlap.loc[len(dfOverlap.index)] = df.iloc[i]
    elif df['event'][i] in UniqueEvents:
        dfUnique.loc[len(dfUnique.index)] = df.iloc[i]

print(nResolvedHgg)
print(nBoostedHgg)

#dfOverlap.to_pickle('OverlapEvents_genInfo.pkl')
#dfUnique.to_pickle('UniqueEvents_genInfo.pkl')

repeatsFgg = np.array([])
boostedFgg = np.array([])
resolvedFgg = np.array([])
for i in range(len(dfInc)):
    if i % 1000 == 0:
        print("Reached Event: {}".format(i))
    if dfInc['event'][i] in repeatsFgg:
        continue
    else:
        repeatsFgg = np.append(repeatsFgg, [dfInc['event'][i]])
    if dfInc['event'][i] not in fggEvents:
        continue

    if (dfInc['Hbb_pt'][i] < 350) or (dfInc['genBBfromH_delta_R'][i] > 0.8):
        resolvedFgg = np.append(resolvedFgg, [dfInc['event'][i]])
    else:
        boostedFgg = np.append(boostedFgg, [dfInc['event'][i]])
print(len(resolvedFgg))
print(len(boostedFgg))

print(len(np.intersect1d(boostedFgg, boostedHgg)))

