import math
import numpy as np
import pandas
import librosa

from matplotlib import pyplot as plt

import time
import csv


def normalize_feature_sequence(X, norm='2', threshold=0.0001, v=None):
    """Normalizes the columns of a feature sequence

    Notebook: C3/C3S1_FeatureNormalization.ipynb

    Args:
        X (np.ndarray): Feature sequence
        norm (str): The norm to be applied. '1', '2', 'max' or 'z' (Default value = '2')
        threshold (float): An threshold below which the vector ``v`` used instead of normalization
            (Default value = 0.0001)
        v (float): Used instead of normalization below ``threshold``. If None, uses unit vector for given norm
            (Default value = None)

    Returns:
        X_norm (np.ndarray): Normalized feature sequence
    """
    assert norm in ['1', '2', 'max', 'z']

    K, N = X.shape
    X_norm = np.zeros((K, N))

    if norm == '2':
        if v is None:
            v = np.ones(K, dtype=np.float64) / np.sqrt(K)
        for n in range(N):
            s = np.sqrt(np.sum(X[:, n] ** 2))
            if s > threshold:
                X_norm[:, n] = X[:, n] / s
            else:
                X_norm[:, n] = v
    else:
        raise ValueError("Norm type not supported")

    return X_norm


def compute_features(audio, sr, hop_length=512, n_mfcc=13, n_fft=None):
    # if n_fft is None:
    #     n_fft = next_power_of_2(hop_length)

    mfcc = librosa.effects.feature.mfcc(y=audio, sr=sr, hop_length=hop_length, n_mfcc=n_mfcc)
    # Normalize using Euclidean norm - as the diagonal matching code expects it
    mfcc = normalize_feature_sequence(mfcc)
    return mfcc


def cost_matrix_dot(X, Y):
    """Computes cost matrix via dot product

    Notebook: C7/C7S2_DiagonalMatching.ipynb

    Args:
        X (np.ndarray): First sequence (K x N matrix)
        Y (np.ndarray): Second sequence (K x M matrix)

    Returns:
        C (np.ndarray): Cost matrix
    """
    ret = 1 - X.T @ Y
    return ret


def matching_function_diag(C, cyclic=False):
    """Computes diagonal matching function

    Notebook: C7/C7S2_DiagonalMatching.ipynb

    Args:
        C (np.ndarray): Cost matrix
        cyclic (bool): If "True" then matching is done cyclically (Default value = False)

    Returns:
        Delta (np.ndarray): Matching function
    """
    N, M = C.shape
    Delta = C[0, :]
    for n in range(1, N):
        Delta = Delta + np.roll(C[n, :], -n)
    Delta = Delta / N
    if cyclic is False:
        Delta[M - N + 1:M] = np.inf
    return Delta


def mininma_from_matching_function(Delta, rho=2, tau=0.2, num=None):
    """Derives local minima positions of matching function in an iterative fashion

    Notebook: C7/C7S2_DiagonalMatching.ipynb

    Args:
        Delta (np.ndarray): Matching function
        rho (int): Parameter to exclude neighborhood of a matching position for subsequent matches (Default value = 2)
        tau (float): Threshold for maximum Delta value allowed for matches (Default value = 0.2)
        num (int): Maximum number of matches (Default value = None)

    Returns:
        pos (np.ndarray): Array of local minima
    """
    global target_keys
    st = time.time()
    Delta_tmp = np.array(Delta).copy()
    M = len(Delta)
    pos = []
    num_pos = 0
    rho = int(rho)
    if num is None:
        num = M

    min_dict = {}

    while num_pos < num and np.sum(Delta_tmp < tau) > 0:
        m = np.argmin(Delta_tmp)
        min_dict[m] = Delta_tmp[m]
        pos.append(m)
        num_pos += 1
        # exclude this region from candidate minimums
        s = max(0, m - rho)
        e = min(m + rho, M)
        # print(s, e)
        Delta_tmp[s:e] = np.inf

    target_keys = [key for key, value in min_dict.items()]

    percentage_changes = calculate_percentage(min_dict, Delta)

    target_values = [value for value in percentage_changes.values() if value > 1]
    target_keys = [key for key, value in percentage_changes.items() if value in target_values]

    pos = np.array(target_keys).astype(int)
    return pos


def calculate_percentage(min_dict, Delta):
    percentage_changes = {}

    keys = list(min_dict.keys())

    for i in range(len(keys)):
        current_value = Delta[keys[i]]
        next_value = Delta[keys[i] + 1]
        if math.isinf(next_value):
            continue
        percentage_change = ((next_value - current_value) / current_value) * 100
        percentage_changes[keys[i]] = percentage_change

    return percentage_changes


def next_power_of_2(x):
    return 2 ** (math.ceil(math.log(x, 2)))


def plot_results(scores, threshold=None, events=None):
    fig, ax = plt.subplots(1, figsize=(30, 5))
    ax.plot(scores.reset_index()['time'], scores['distance'])

    if threshold is not None:
        ax.axhline(threshold, ls='--', alpha=0.5, color='black')

    if events is not None:
        for idx, e in events.iterrows():
            ax.axvspan(e['start'], e['end'], color='green', alpha=0.5)

    import matplotlib.ticker
    x_formatter = matplotlib.ticker.FuncFormatter(ticker_format_minutes_seconds)
    ax.xaxis.set_major_formatter(x_formatter)
    ax.xaxis.set_major_locator(matplotlib.ticker.MultipleLocator(base=10 * 60))
    ax.xaxis.set_minor_locator(matplotlib.ticker.MultipleLocator(base=60))
    ax.grid(axis='x')
    ax.grid(axis='x', which='minor')

    return fig


def ticker_format_minutes_seconds(x, pos):
    hours = int(x // 3600)
    minutes = int((x % 3600) // 60)
    seconds = int(x % 60)

    return "{:02d}:{:02d}:{:02d}".format(hours, minutes, seconds)


def find_audio(long, short, sr=22050, time_resolution=0.500, max_matches=6, score_threshold=0.17):
    query = compute_features(short, sr=sr)
    clip = compute_features(long, sr=sr)

    C = cost_matrix_dot(query, clip)

    Delta = matching_function_diag(C)

    scores = pandas.DataFrame({
        'time': librosa.times_like(Delta, hop_length=512, sr=22050),
        'distance': Delta,
    }).set_index('time')

    match_idx = mininma_from_matching_function(scores['distance'].values,
                                               num=max_matches, rho=query.shape[1], tau=score_threshold)

    matches = scores.reset_index().loc[match_idx]
    matches = matches.rename(columns={'time': 'start'})
    matches['end'] = matches['start'] + 60
    matches = matches.reset_index()

    return scores, matches


def find_matches_result(master_file, short_file, short_offset):
    long, _ = librosa.load(master_file)
    short, _ = librosa.load(short_file, offset=short_offset*60, duration=60)
    # long, _ = librosa.load(master_file, offset=long_offset, duration=60 * 6)
    # short, _ = librosa.load(short_file, offset=initial_minute * 60, duration=60)

    _, matches = find_audio(long, short, max_matches=6, score_threshold=0.17)
    return matches

# fst = time.time()
# threshold = 0.17
# max_matches = 6
#
# # long_file_name = './master_folder/Somoy TV 1-0-20230606110227_11AM/5-15_Somoy TV 1-0-20230606110227_11AM.wav'
# long_file_directories = ['./master_folder/GTV_12-0-20230606130235_1PM',
#                          './master_folder/Channel-i 4-0-20230606130124_1PM',
#                          './master_folder/Somoy TV 1-0-20230606130229_1PM']
# short_file_directories = ['./device_folder/audio_2023-06-06_11-59-38',
#                           './device_folder/audio_2023-06-06_12-04-46',
#                           './device_folder/audio_2023-06-06_12-09-55',
#                           './device_folder/audio_2023-06-06_12-15-07',
#                           './device_folder/audio_2023-06-06_12-20-16',
#                           './device_folder/audio_2023-06-06_12-25-24',
#                           './device_folder/audio_2023-06-06_12-30-33',
#                           './device_folder/audio_2023-06-06_12-35-43',
#                           './device_folder/audio_2023-06-06_12-40-50',
#                           './device_folder/audio_2023-06-06_12-45-58',
#                           './device_folder/audio_2023-06-06_12-51-07',
#                           './device_folder/audio_2023-06-06_12-56-18']
# short_file_name = ''
#
# # long, long_sr = librosa.load(long_file_name)
# csv_file = open('/Users/hafizur_admin/Desktop/workstation/code/personal/audioMatching/test-folder/12PM.csv', 'w')
# writer = csv.writer(csv_file, delimiter=',', escapechar=' ', quoting=csv.QUOTE_NONE)
#
# for lfn in range(len(long_file_directories)):
#     print(long_file_directories[lfn])
#     print("***" * 30)
#     current_dir = os.getcwd()
#     target_mas_dir = os.path.join(current_dir, long_file_directories[lfn])
#     os.chdir(target_mas_dir)
#     for master_file in os.listdir(target_mas_dir):
#         if master_file.startswith('.'):
#             continue
#         os.chdir(current_dir)
#         master_file_name = long_file_directories[lfn] + "/" + master_file
#         long, long_sr = librosa.load(master_file_name)
#         for i in range(len(short_file_directories)):
#             current_dir = os.getcwd()
#             target_dev_dir = os.path.join(current_dir, short_file_directories[i])
#             os.chdir(target_dev_dir)
#             for file in os.listdir(target_dev_dir):
#                 short_file_name = short_file_directories[i] + "/" + file
#                 if file.startswith('.'):
#                     continue
#                 short, short_sr = librosa.load(file)
#                 start_time = time.time()
#                 scores, matches = find_audio(long, short, max_matches=max_matches, score_threshold=threshold)
#                 end_time = time.time()
#                 execution_time = end_time - start_time
#                 print_statement = f'long file {master_file_name} , short file {short_file_name} , no match , execution time {execution_time}'
#
#                 if matches.empty:
#                     print(print_statement)
#
#                 for idx, m in matches.iterrows():
#                     # if Decimal(m['start']) > 540:
#                     #     print(f'long file {master_file_name} | short file {short_file_name} | no match | execution time {execution_time}')
#                     #     continue
#                     td = pandas.Timedelta(m['start'], unit='s').round('1s').to_pytimedelta()
#                     tend = pandas.Timedelta(m['end'], unit='s').round('1s').to_pytimedelta()
#                     print_statement = f'long file {master_file_name} , short file {short_file_name} , match start {td} , match end {tend} , execution time {execution_time}'
#                     print(print_statement)
#
#                 writer.writerow([print_statement])
#
#             os.chdir(current_dir)
#
# csv_file.close()
#
# lst = time.time()
# print(f'final exec time {lst - fst}')
