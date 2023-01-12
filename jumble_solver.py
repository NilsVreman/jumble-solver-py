from typing import List, Dict
import sys
import requests
import os


class AnagramFinder:
    """ Python implementation for a jumble solver (anagram finder).

    The AnagramFinder class takes a word list as constructor input.
    Each word in the word list is converted to a prime number multiplication,
    where each character represent a unique prime number,
    e.g., 'a' = 2, 'b' = 3, 'c' = 5, etc. With this representation, an anagram
    of a `word` is any `other_word` where all prime number factors are
    represented in the original `word`.

    Complexity Analysis:
        n: Number of words in word list
        m: Average word length
        * Parsing word list:
            + Reading all words: O(n)
            + Convert a word to nbr: O(m)
            = Total: O(n*m)
        * Finding all anagrams:
            + Convert the searched word to nbr: O(m)
            + Iterate parsed data: O(n)
            = Total: O(n+m) = O(n)

    Example:
        word              = "dog"   # number repr: 'd' = 7, 'o' = 47, 'g' = 17
        word_as_nbr       = 7*47*17
        other_word        = "go"
        other_word_as_nbr = 17*47
        other_word_is_sub_anagram = word_as_nbr % other_word_as_nbr == 0 # True
    """

    def __init__(self, word_list: List[str]):
        """
        Attributes:
            __word_to_prime_mapper (__WordToNumberMapper): An object that maps a
                word into a number.
            _word_dict (Dict[int, List[str]]): Maps a number representation to a
                list of words with that value
            _cached_anagrams (Dict[str, List[str]]): A cache of already computed
                anagrams.
        """
        self.__word_to_nbr_mapper = self.__WordToNumberMapper()
        self._word_dict: Dict[int, List[str]] = dict()
        for word in word_list:
            word = word.lower()
            if not word.isalpha():
                continue
            nbr_repr = self.__word_to_nbr_mapper.map(word)
            self._word_dict.setdefault(nbr_repr, []).append(word)
        self._cached_anagrams: Dict[str, List[str]] = dict()

    def find_sub_and_full_anagrams(self, word: str) -> List[str]:
        """ Compute all sub- and full anagrams for input 'word'.

        Args:
            word (str): Word to find anagrams for.

        Returns:
            List[str]: A list of sub- and full anagrams of input word.
        """
        if not word.isalpha():
            _terminate("Words must contain nothing but letters!")

        if word in self._cached_anagrams:
            return self._cached_anagrams[word]

        anagrams = self._find_all_anagrams_for_word(word)
        self._cached_anagrams[word] = anagrams
        return anagrams

    def _find_all_anagrams_for_word(self, word: str) -> List[str]:
        """ Find all sub- and full anagrams of `word` using its prime number
        representation """
        nbr_repr = self.__word_to_nbr_mapper.map(word)
        # if nbr_repr contains at least all prime factors of other_word_as_nbr,
        # then other_word_as_nbr is an anagram of nbr_repr, hence use of modulo
        all_anagrams: List[str] = [
            anagram
            for other_word_as_nbr in self._word_dict.keys()
            if nbr_repr % other_word_as_nbr == 0
            for anagram in self._word_dict[other_word_as_nbr]
        ]
        all_anagrams.remove(word)
        return all_anagrams

    class __WordToNumberMapper:
        """
        Maps every character in a word to a prime number.
        A words's character configuration is therefore
        represented as a prime number multiplication.
        """

        def __init__(self):
            """
            Attributes:
                _prime_dict (Dict[str, int]): Dict of (char => prime nbr) pairs
            """
            prime_list = self.__list_first_n_primes(26)
            self._prime_dict = {
                c: prime_list[i]
                for i, c in enumerate("abcdefghijklmnopqrstuvwxyz")
            }

        def __list_first_n_primes(self, n: int) -> List[int]:
            """ Returns a list of n primes """
            primes = [2]
            while len(primes) < n:
                prime_candidate = primes[-1]
                found_new_prime = False
                while not found_new_prime:
                    found_new_prime = True
                    prime_candidate += 1
                    for prime in primes:
                        if prime_candidate % prime == 0:
                            found_new_prime = False
                            break
                    if found_new_prime:
                        primes.append(prime_candidate)
            return primes

        def map(self, word: str) -> int:
            """ Map a string to the corresponding number representation """
            result = 1
            for char in word:
                result *= self._prime_dict[char]
            return result


def read_file_into_word_list(file_path: str) -> List[str]:
    """ Read the contents of file_path into a list of words """
    try:
        with open(file_path, "r") as file:
            return file.read().splitlines()
    except IOError:
        _terminate("File \"{}\" not found in path".format(file_path))


def download_word_list(url: str, target_path: str):
    """ Download the wordlist from url (unless it already exists) """
    if os.path.exists(target_path):
        return

    try:
        with requests.get(url, stream=True) as response:
            # Open stream to url and raise error if something failed
            response.raise_for_status()
            words_data = response.text
    except requests.exceptions.ConnectionError:
        _terminate("Couldn't open link to webpage \"{}\"".format(url))
    except requests.exceptions.HTTPError:
        _terminate("Webpage \"{}\" doesn't exist".format(url))

    with open(target_path, "w") as file:
        file.write(words_data)


def _validate_cmd_line_input():
    if len(sys.argv) != 3:
        _terminate("Wrong number of input arguments!")
    return sys.argv[1], sys.argv[2]


def _terminate(msg: str):
    print(msg)
    sys.exit(0)


def main():
    file_path, search_word = _validate_cmd_line_input()
    download_word_list("http://www.mieliestronk.com/corncob_lowercase.txt",
                       file_path)
    word_list = read_file_into_word_list(file_path)
    anagram_finder = AnagramFinder(word_list)
    anagrams = anagram_finder.find_sub_and_full_anagrams(search_word)
    for anagram in anagrams:
        print(anagram)


if __name__ == "__main__":
    main()
