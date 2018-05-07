"""Tell some fun facts"""
import random
import time
import os
import snowboydecoder
from flite import flite

facts = [
    "If they have ample water, cats can tolerate temperatures up to 133°F.",
    "On average, cats spend 15-20 hours per day sleeping! That means they are only active for 4-8 hours per day, some even less!",
    "Unlike dogs, cats do not have a sweet tooth. Scientists believe this is due to a mutation in a key taste receptor.",
    "When a cat chases its prey, it keeps its head level. Dogs and humans bob their heads up and down.",
    "Female cats tend to be right-pawed, while male cats are more often left-pawed. Interestingly, while 90% of humans are right-handed, the remaining 10% of lefties also tend to be male.",
    "A cat can’t climb head first down a tree because every claw on a cat’s paw points the same way. To get down from a tree, a cat must back down.",
    "Cats make about 100 different sounds. Dogs make only about 10.",
    "A cat’s brain is biologically more similar to a human brain than it is to a dog’s. Both humans and cats have identical regions in their brains that are responsible for emotions.",
    "There are more than 500 million domestic cats in the world, with approximately 40 recognized breeds.",
    "During the time of the Spanish Inquisition, Pope Innocent VIII condemned cats as evil and thousands of cats were burned. Unfortunately, the widespread killing of cats led to an explosion of the rat population, which exacerbated the effects of the Black Death.",
    "During the Middle Ages, cats were associated with witchcraft, and on St. John’s Day, people all over Europe would stuff them into sacks and toss the cats into bonfires. On holy days, people celebrated by tossing cats from church towers.",
    "Cats are North America’s most popular pets: there are 73 million cats compared to 63 million dogs. Over 30% of households in North America have a cat.",
    "According to Hebrew legend, Noah prayed to God for help protecting all the food he stored on the ark from being eaten by rats. In reply, God made the lion sneeze, and out popped a cat.",
    "A cat’s hearing is better than a dog’s. A cat can hear high-frequency sounds up to two octaves higher than a human.",
    "A cat can travel at a top speed of approximately 31 miles per hour over a short distance.",
    "A cat can jump up to five times its own height in a single bound.",
    "Some cats have survived falls of over 65 feet, due largely to their “righting reflex.” The eyes and balance organs in the inner ear tell it where it is in space so the cat can land on its feet. Even cats without a tail have this ability.",
    "A cat rubs against people not only to be affectionate but also to mark out its territory with scent glands around its face. The tail area and paws also carry the cat’s scent. ",
    "Researchers are unsure exactly how a cat purrs. Most veterinarians believe that a cat purrs by vibrating vocal folds deep in the throat. To do this, a muscle in the larynx opens and closes the air passage about 25 times per second.",
    "When a family cat died in ancient Egypt, family members would mourn by shaving off their eyebrows. They also held elaborate funerals during which they drank wine and beat their breasts. The cat was embalmed with a sculpted wooden mask and the tiny mummy was placed in the family tomb or in a pet cemetery with tiny mummies of mice.",
    "Most cats give birth to a litter of between one and nine kittens. The largest known litter ever produced was 19 kittens, of which 15 survived.",
    "The biggest wildcat today is the Siberian Tiger. It can be more than 12 feet long (about the size of a small car) and weigh up to 700 pounds.",
    "The smallest wildcat today is the Black-footed cat. The females are less than 20 inches long and can weigh as little as 2.5 lbs.",
    "Many Egyptians worshiped the goddess Bast, who had a woman’s body and a cat’s head.",
    "Mohammed loved cats and reportedly his favorite cat, Muezza, was a tabby. Legend says that tabby cats have an “M” for Mohammed on top of their heads because Mohammad would often rest his hand on the cat’s head.",
    "Approximately 1/3 of cat owners think their pets are able to read their minds. ",
    "Some Siamese cats appear cross-eyed because the nerves from the left side of the brain go mostly into the right eye and the nerves from the right side of the brain go mostly to the left eye. This causes some double vision, which the cat tries to correct by “crossing” its eyes.",
    "Cats hate the water because their fur does not insulate well when it’s wet. The Turkish Van, however, is one cat that likes swimming. Bred in central Asia, its coat has a unique texture that makes it water resistant.",
    "The Egyptian Mau is probably the oldest breed of cat. In fact, the breed is so ancient that its name is the Egyptian word for “cat.”",
    "The costliest cat ever is named Little Nicky, who cost his owner $50,000. He is a clone of an older cat.",
    "A cat usually has about 12 whiskers on each side of its face.",
    "A cat’s eyesight is both better and worse than humans. It is better because cats can see in much dimmer light and they have a wider peripheral view. It’s worse because they don’t see color as well as humans do. Scientists believe grass appears red to cats.",
    "In the original Italian version of Cinderella, the benevolent fairy godmother figure was a cat.",
    "The little tufts of hair in a cat’s ear that help keep out dirt, direct sounds into the ear, and insulate the ears are called “ear furnishings.”",
    "The ability of a cat to find its way home is called “psi-traveling.” Experts think cats either use the angle of the sunlight to find their way or that cats have magnetized cells in their brains that act as compasses.",
    "Isaac Newton invented the cat flap. Newton was experimenting in a pitch-black room. Spithead, one of his cats, kept opening the door and wrecking his experiment. The cat flap kept both Newton and Spithead happy.",
    "While many parts of Europe and North America consider the black cat a sign of bad luck, in Britain and Australia, black cats are considered lucky. ",
    "A cat’s jaw can’t move sideways, so a cat can’t chew large chunks of food.",
    "A cat almost never meows at another cat, mostly just humans. Cats typically will spit, purr, and hiss at other cats.",
    "A cat’s back is extremely flexible because it has up to 53 loosely fitting vertebrae. Humans only have 34.",
    "The world’s rarest coffee, Kopi Luwak, comes from Indonesia where a wildcat known as the luwak lives. The cat eats coffee berries and the coffee beans inside pass through the stomach. The beans are harvested from the cats excrement and then cleaned and roasted. Kopi Luwak sells for about 500 dollarts per pound.",
    "Two members of the cat family are distinct from all others: the clouded leopard and the cheetah. The clouded leopard does not roar like other big cats, nor does it groom or rest like small cats. The cheetah is unique because it is a running cat; all others are leaping cats. They are leaping cats because they slowly stalk their prey and then leap on it.",
    "In Japan, cats are thought to have the power to turn into spirits when they die. This may be because according to the Buddhist religion, the body of the cat is the temporary resting place of very spiritual people.",
    "Most cats had short hair until about 100 years ago when it became fashionable to own cats and experiment with breeding.",
    "Cats have 32 muscles that control the outer ear (humans have only 6). A cat can independently rotate its ears 180 degrees.",
    "One reason that kittens sleep so much is that a growth hormone is released only during sleep.",
    "The oldest cat on record was Crème Puff from Austin, Texas, who lived from 1967 to August 6, 2005, three days after her 38th birthday. A cat can typically live up to 20 years, which is equivalent to about 96 human years.",
    "A cat has 230 bones in its body. A human has 206. A cat has no collarbone, so it can fit through any opening the size of its head.",
    "A cat’s nose pad is ridged with a unique pattern, just like the fingerprint of a human. ",
    "Every year, nearly four million cats are eaten in Asia.",
    "Foods that should not be given to cats include onions, garlic, green tomatoes, raw potatoes, chocolate, grapes, and raisins. Though milk is not toxic, it can cause an upset stomach and gas. Tylenol and aspirin are extremely toxic to cats, as are many common house plants. Feeding cats dog food or canned tuna thats for human consumption can cause malnutrition.",
    "A 2007 Gallup poll revealed that both men and women were equally likely to own a cat.",
    "A cat’s heart beats nearly twice as fast as a human heart, at 110 to 140 beats a minute.",
    "Cats don’t have sweat glands over their bodies like humans do. Instead, they sweat only through their paws.",
    "Cats spend nearly 1/3 of their waking hours cleaning themselves.",
    "Cats are extremely sensitive to vibrations. Cats are said to detect earthquake tremors 10 or 15 minutes before humans can.",
    "In contrast to dogs, cats have not undergone major changes during their domestication process.",
    "A female cat is called a queen or a molly.",
    "There are up to 60 million feral cats in the United States alone.",
    "The claws on the cat’s back paws aren’t as sharp as the claws on the front paws because the claws in the back don’t retract and, consequently, become worn.",
    "Cats have whiskers on the backs of their front legs.",
    "Cats are the only mammals unable to taste sweetness.",
    "Cats are actually able to taste scents through the air.",
    "Cats have nearly double the number of neurons in their cerebral cortex than dogs do.",
    "Cats have the biggest eyes relative to the size of their head of any mammal.",
    "Cats can lick a bone perfectly clean with their rough tongues.",
    "Cats and giraffes are the only known animals to move both of their right feet then both of their left feet when walking.",
    "A cats average life expectancy increased by a whole year between 2002 and 2012.",
    "Cats have 1,000 times more data storage than an iPad.",
    "Cats are crepuscular beings, meaning that theyre most active at dawn and dusk.",
    "Cats live longer if kept inside.",
    "A cat will refuse food it doesnt like to the point of starvation.",
    "A lot of cats are actually lactose intolerant.",
    "Female cats can get pregnant from as young as 4 months old.",
    "Catnip produces an effect on your cat that is similar to the way LSD or cannabis effect humans.",
    "Neutered male cats need to consume fewer calories each day.",
    "Cats with question mark tails are in a playful mood.",
    "If a cat blinks slowly at you, it shows that it trusts you and is happy.",
    "Cats take direct eye contact as a threat.",
    "Cats like to sleep on things that smell like their owner.",
    "If a cat attacks your ankles, its probably doing so out of boredom.",
    "Cats love laundry baskets because theyre good hiding spots that provide them with peepholes.",
    "Cats really hate the smell of citrus.",
    "Certain cats adore the smell of chlorine.",
    "As strange as it sounds, a green cat was actually once born in Denmark.",
    "Abraham Lincoln lived with 4 cats in the White House.",
    "Bill Clintons cat, Socks, was said to receive more letters than the President himself.",
    "The mayor of Alaskas Talkeetna district is a cat called Stubbs.",
    "A cat purrs at a frequency of 25 to 150 Hertz.",
    "A group of kittens is known as a kindle.",
    "Cat breeders are called catteries.",
    "A trained cat could easily beat Usain Bolt in the 200-meter dash.",
    "Cats are actually able to drink seawater in order to survive.",
    "Cats often dream.",
    "Cats have driven at least 33 species extinct.",
    "Cats perceive humans as large, hairless cats.",
    "Cats didnt exist in the Americas until Europeans brought them there to exterminate mice.",
    "Most world languages have a similar-sounding word to describe cats meow sound.",
    "The first domesticated cats first appeared at around 3600 BC.",
    "The first-ever cat video was recorded in 1894.",
]
  
def fun_fact(handler):
    prefixes = ["Fun fact", "Did you know", "I bet you dont know",  "Here is a neat tidbit",
           "I know a secret", "I bet Karthik 1 didnt know"]
    pfx = random.choice(prefixes)
    fact = random.choice(facts)
    wav1 = flite(pfx)
    wav2 = flite(fact)
    handler.play_audio([wav1, wav2], pfx + ": " + fact)

class FunFacts:
    """Show a fun fact"""
    def __init__(self, cbhandler):
        self.cbhandler = cbhandler

    def do_fact(self, *args):
        fun_fact(self.cbhandler)

if __name__ == "__main__":
    fun_fact()

