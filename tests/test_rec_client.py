# TODO fix
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


from clients.recommend_client import get_recommendation
import json


if __name__ == "__main__":
    test_dict = {
        "interview_description": "Dziś pierwszy raz napady drgawkowe z niecałkowitą utratą przytomności, pierwszy o godzinie 18:20. W trakcie ataku pies otwierał szeroko oczy i głęboko oddychał, pomiędzy atakami całkowita utrata przytomności, nie oddał ani kału ani moczu. Każdy z ataków trwał około 30-40 sekund. Do godziny 21:00 około 7 ataków. Ostatni posiłek jadł rano, ma stały dostęp do karmy. Pies nie ma dostępu do trucizn ani nawozów, mieszka w kojcu, dziś rano jadł standardowe jedzenie. Około miesiąc temu przebył babeszjozę potwierdzoną w gabinecie weterynaryjnym, otrzymał dwie kroplówki dożylne, nie kontynuowano leczenia. Wcześniej nie wykazywał niepokojących objawów. Jest psem adoptowanym, właściciele nie znają jego wcześniejszych losów, w schronisku nie miał ataków, wcześniej silne zapalenie płuc. Zaszczepiony przeciwko wściekliźnie i chorobom wirusowym. Pies jest agresywny. Dziś przywieziony nieprzytomny, mokry, właścicielka schładzała polewając wodą.",
        "treatment_description": "Podłączono psa do maski tlenowej, założono wkłucie dożylne, pobrano krew na szeroki profil z jonogramem, podano Płyn Ringera 600 ml w tempie 400 ml/h, w trakcie ataku podano propofol 4,5 ml i.v., następnie dodatkowo 1 ml propofolu i.v. Odbyły się badania laboratoryjne (krew, T4, fT4), monitorowano parametry życiowe. Przygotowano psa do wyjazdu do lecznicy całodobowej na monitoring.",
        "applied_medicines": "Propofol-Lipuro 10mg/1ml 5,5 ml, Płyn Ringera 600 ml",
        "recommendation": "Nocny monitoring w lecznicy całodobowej, diagnostyka w celu wykluczenia zaburzeń kardiologicznych oraz pełne badanie neurologiczne po odzyskaniu przez psa przytomności. Oczekiwanie na wynik oznaczenia hormonów tarczycy. Kontakt w tej sprawie z lecznicą.",
    }

    interview_description = test_dict["interview_description"]
    treatment_description = test_dict["treatment_description"]

    result = get_recommendation(interview_description, treatment_description)

    print("\n✔ Result JSON:")
    print(json.dumps(result, indent=4, ensure_ascii=False))
