extern crate aho_corasick;

use aho_corasick::{AcAutomaton, Automaton};
use aho_corasick::Matches as AhoMatches;
use words::WORDS;
pub use words::Lang;

mod words;

pub struct Filter {
    automaton: AcAutomaton<&'static str>,
}

impl Filter {
    pub fn new(langs: Option<Vec<Lang>>) -> Filter {
        let automaton = if let Some(langs) = langs {
            langs.into_iter().flat_map(|lang| WORDS[lang as usize]).map(|words| *words).collect()
        } else {
            WORDS.iter().flat_map(|words| words.iter()).map(|words| *words).collect()
        };

        Filter {
            automaton: automaton,
        }
    }

    pub fn find<'a>(&'a self, s: &'a str) -> Matches {
        Matches {
            input: s,
            it: self.automaton.find(s),
        }
    }
}

pub struct Matches<'a, 's> {
    input: &'a str,
    it: AhoMatches<'a, 's, &'static str, AcAutomaton<&'static str>>,
}

impl<'a, 's> Iterator for Matches<'a, 's> {
    type Item = (&'a str, usize, usize);

    fn next(&mut self) -> Option<Self::Item> {
        self.it
            .next()
            .map(|m| (&self.input[m.start..m.end], m.start, m.end))
    }
}

#[cfg(test)]
mod test {
    use super::{Filter, Lang};

    #[test]
    fn test_none() {
        let filter = Filter::new(Some(vec![]));
        let mut iter = filter.find("La drague en haute mer.");

        assert!(iter.next().is_none());
    }

    #[test]
    fn test_english_absent() {
        let filter = Filter::new(Some(vec![Lang::EN]));
        let mut iter = filter.find("La drague en haute mer.");

        assert_eq!(iter.next(), None);
    }

    #[test]
    fn test_all() {
        let filter = Filter::new(None);
        let mut iter = filter.find("La drague en haute mer.");

        assert_eq!(iter.next(), Some(("drague", 3, 9)));
    }
}
