from typing import List, Dict
import sys
import requests
import os
import math # NOTE: maybe remove

class AnagramFinder:
    """ AnagramFinder: Python implementation for a jumble solver (anagram finder).
                       Finds sub- and full anagrams of words.

    DETAILED DESCRIPTION:
    The AnagramFinder class takes a word list as constructor input.
    Each word in the word list is converted to a prime number multiplication,
    where each character represent a unique prime number, e.g., 'a' = 2, 'b' = 3, 'c' = 5, etc.
    With this representation, an anagram of a `word` is any `other_word` where all
    prime number factors are represented in the original `word`.

    COMPLEXITY ANALYSIS:
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

    EXAMPLE:
    word              = "dog"   # number representation: 'd' = 7, 'o' = 47, 'g' = 17
    word_as_nbr       = 7*47*17
    other_word        = "go"
    other_word_as_nbr = 17*47
    other_word_is_sub_anagram = word_as_nbr % other_word_as_nbr == 0 # True
    """

    def __init__(self, word_list: List[str]):
        """ CLASS PARAMETERS:
        __word_to_prime_mapper: An object that maps a word into a number equivalent
        _word_dict:             A set of words to use for faster lookups
        _found_anagrams:        A dictionary of already looked up words and their corresponding anagrams
        """
        self.__word_to_nbr_mapper = self.__WordToNumberMapper()
        self._word_dict: Dict[int, List[str]] = dict()
        for word in word_list:
            word = word.lower()
            if not word.isalpha():
                continue
            nbr_repr: int = self.__word_to_nbr_mapper.map(word)
            self._word_dict.setdefault(nbr_repr, []).append(word)
        self._found_anagrams: Dict[str, List[str]] = dict()

    def find_sub_and_full_anagrams(self, word: str) -> List[str]:
        """ Computes all anagrams and subanagrams of the input 'word' and returns them as a list. """
        if not word.isalpha():
            print("Words must contain nothing but letters!")
            _terminate_execution()

        if word in self._found_anagrams:
            return self._found_anagrams[word]

        anagrams: List[str] = self._find_all_anagrams_for_word(word)
        self._found_anagrams[word] = anagrams
        return anagrams

    def _find_all_anagrams_for_word(self, word: str) -> List[str]:
        """ find all sub- and full anagrams of `word` using the prime number representation of the word """
        nbr_repr: int = self.__word_to_nbr_mapper.map(word)
        all_anagrams: List[str] = [anagram
                                   for other_word_as_nbr in self._word_dict.keys()
                                   if self.__word_to_nbr_mapper.is_sub_or_full_anagram(nbr_repr, other_word_as_nbr)
                                   for anagram in self._word_dict[other_word_as_nbr]]
        all_anagrams.remove(word)
        return all_anagrams

    class __WordToNumberMapper:
        """ __WordToNumberMapper: Maps every character in a word to a prime number.
                                  A words's character configuration is therefore
                                  represented as a prime number multiplication.
        """
    
        def __init__(self):
            """ CLASS PARAMETERS:
            _prime_dict: A dict of (char => prime numbers) representing the
                         prime number representation of each character
            """
            prime_list: List[int] = self.__list_first_n_primes(26)
            self._prime_dict: Dict[str, int] = {c: prime_list[i] for i, c in enumerate("abcdefghijklmnopqrstuvwxyz")}

        def __list_first_n_primes(self, n: int) -> List[int]:
            """ Returns a list of n primes """
            primes: List[int] = [2]
            while len(primes) < n:
                i = primes[-1]
                found_new_prime = False
                while not found_new_prime:
                    found_new_prime = True
                    i += 1
                    for prime in primes:
                        if i % prime == 0:
                            found_new_prime = False
                            break
                    if found_new_prime:
                        primes.append(i)
            return primes
            
        #def __list_first_n_primes_sieve(n: int) -> List[int]:
        #    """ Returns a list of n primes """
        #    N = int(n*math.log(n) + n*math.log(math.log(n)))
        #    sieve = [True] * N
        #    for i in range(3,int(N**0.5)+1, 2):
        #        if sieve[i]:
        #            sieve[i*i::2*i] = [False]*((N-i*i-1) // (2*i)+1)
        #    primes = [2] + [i for i in range(3, N, 2) if sieve[i]]
        #    return primes[:n]

        def map(self, word: str) -> int:
            """ Map a string to the corresponding number representation """
            res_nbr = 1
            for c in word:
                res_nbr *= self._prime_dict[c]
            return res_nbr

        def is_sub_or_full_anagram(self, src_repr: int, cmp_repr: int) -> bool:
            """ Check if cmp_repr is a sub or full anagram of src_repr """
            return src_repr % cmp_repr == 0

        #def is_sub_or_full_anagram_str(self, src_word: str, cmp_word: str) -> bool:
        #    """ Check if cmp_word is a sub or full anagram of src_word """
        #    cmp_repr: int = self.map(cmp_word)
        #    src_repr: int = self.map(src_word)
        #    return src_repr % cmp_repr == 0
            
def read_file_into_word_list(file_path: str) -> List[str]:
    """ Read the contents of file_path into a list of words """
    try:
        with open(file_path, "r") as file:
            return file.read().splitlines()
    except IOError as e:
        print("File \"{}\" not found in path".format(file_path))
        _terminate_execution()

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
        print("Couldn't open link to webpage \"{}\"".format(url))
        _terminate_execution()
    except requests.exceptions.HTTPError:
        print("Webpage \"{}\" doesn't exist".format(url))
        _terminate_execution()

    with open(target_path, 'w') as file:
        file.write(words_data)
    

def _validate_cmd_line_input():
    if len(sys.argv) != 3:
        print("Wrong number of input arguments!")
        _terminate_execution()

    return sys.argv[1], sys.argv[2]

def _terminate_execution():
    print("Terminating execution")
    sys.exit(0)

def main():
    file_path, search_word = _validate_cmd_line_input()
    download_word_list("http://www.mieliestronk.com/corncob_lowercase.txt", file_path)
    word_list: List[str] = read_file_into_word_list(file_path)
    anagram_finder: AnagramFinder = AnagramFinder(word_list)
    anagrams: List[str] = anagram_finder.find_sub_and_full_anagrams(search_word)
    for anagram in anagrams:
        print(anagram)

if __name__ == "__main__":
    main()
