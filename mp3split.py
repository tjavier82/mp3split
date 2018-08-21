


# TODO: Implement a threaded function


from pydub import AudioSegment
import os
import argparse
import logging

VERBOSE_MODE = False
DEFAULT_DURATION = 600.0
OVERWRITE = False
LOGGER_NAME = 'mp3split_log'


def set_up_logs(verbosity):
    # create logger
    logger = logging.getLogger(LOGGER_NAME)
    if verbosity:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.ERROR)

    # create console handler and set level to debug
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)

    # create formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # add formatter to ch
    ch.setFormatter(formatter)

    # add ch to logger
    logger.addHandler(ch)

    return logger


def create_new_dir (filename):
    logger = logging.getLogger(LOGGER_NAME)
    new_dir = os.path.splitext(filename)[0]
    logger.debug('creating ' + new_dir)
    try:
        os.mkdir(new_dir)
    except FileExistsError:
        logger.info (new_dir + ' already exists')
    return new_dir


def iterate_on_a_directory (directory, duration):
    """"
    Get a directory and calls the splitter function on each valid file.
    Note this is not recursive.
    """
    logger = logging.getLogger(LOGGER_NAME)
    logger.debug('working on ' + directory)
    logger.debug(os.listdir(directory))
    for f in os.listdir(directory):
        file_name = os.path.join(directory, f)
        if os.path.isfile(file_name):
            file_extension = os.path.splitext(file_name)[1]
            if file_extension.lower() == ".mp3":
                logger.debug('calling splitter funtion with ' + file_name + ' and ' + str(duration))
                sequential_split(file_name, duration)
            else:
                logger.info(file_name + 'is not a mp3 file. Ignoring it')
    return


# def multithread_split(filename, duration):
#     """
#     Given a mp3 filename and a duration, splits the file on n files
#     with duration each.
#     Multithread implementation
#     """
#     logger = logging.getLogger(LOGGER_NAME)
#
#     logger.debug('opening ' + filename)
#     song = AudioSegment.from_mp3(filename)
#
#     new_dir = create_new_dir(filename)
#
#     length = song.duration_seconds * 1000 # slicing is in milisencods
#     duration = duration * 1000
#     number_files = int (length/duration)
#     if length % duration > 0:
#         number_files += 1
#
#     logger.debug('mp3 file duration is ' + str(length/1000) + ' seconds')
#     logger.debug(str(number_files) + ' files will be created')



def sequential_split(filename, duration):
    """
    Given a mp3 filename and a duration, splits the file on n files
    with duration each.
    Sequential implementation
    """
    logger = logging.getLogger(LOGGER_NAME)

    logger.debug('opening ' + filename)
    song = AudioSegment.from_mp3(filename)

    new_dir = create_new_dir(filename)

    length = song.duration_seconds * 1000 # slicing is in milisencods
    duration = duration * 1000
    number_files = int (length/duration)
    if length % duration > 0:
        number_files += 1

    logger.debug('mp3 file duration is ' + str(length/1000) + ' seconds')
    logger.debug(str(number_files) + ' files will be created')

    i = 0
    iteration = 1

    while i < length:
        j = i + duration
        slice = song[i:j]
        i = j
        new_file_name = os.path.join(new_dir, (os.path.splitext(os.path.basename(filename))[0] +
                                               str(iteration).zfill(3) + '.mp3'))
        logging.debug ('creating ' + new_file_name)
        if os.path.isfile(new_file_name):
            if OVERWRITE:
                logger.debug(new_file_name + ' already exists. Overwriting it')
                try:
                    slice.export(new_file_name, format='mp3')
                except:
                    logger.error('Exception creating ' + new_file_name + '. Exiting...')
                    exit(1)
            else:
                logger.debug(new_file_name + ' already exists. Ignoring it')
        else:
            try:
                slice.export(new_file_name, format='mp3')
            except:
                logger.error('Exception creating ' + new_file_name + '. Exiting...')
                exit(1)
        iteration += 1

    return


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("filename", help="mp3 file you want to split")
    parser.add_argument("-d", "--duration", help="duration in seconds for each piece", type=float,
                        default=DEFAULT_DURATION)
    parser.add_argument("-v", "--verbose", help="increase verbosity", action="store_true")
    parser.add_argument("-o", "--overwrite", help="overwrites outputfiles if they exist", action="store_true")
    args = parser.parse_args()

    logger = set_up_logs(args.verbose)

    if args.overwrite:
        OVERWRITE = True

    # Sanity checks
    if args.duration is 0.0:
        logger.error('duration can not be zero.')
        exit(1)

    if not (os.path.exists(args.filename)):
        logger.error(args.filename + ' does not exist')
        exit(1)

    if os.path.isdir(args.filename):
        iterate_on_a_directory(args.filename, args.duration)
    else:
        file_extension = os.path.splitext(args.filename)[1]
        if file_extension.lower() != ".mp3":
            logger.error('extension ' + file_extension + ' not supported.')
            exit(1)
        else:
            sequential_split(args.filename, args.duration)
