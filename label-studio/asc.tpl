<View>
  <Image name="img" value="$image"></Image>
  <Labels name="polarity" toName="text">
    <Label alias="p" value="positive" background="green"/>
    <Label alias="ne" value="negative" background="red"/>
    <Label alias="nl" value="neutral" background="gray"/>
    <Label alias="u" value="unknown" background="black"/>
  </Labels>
  <Text name="text" value="$text"/>
</View>
